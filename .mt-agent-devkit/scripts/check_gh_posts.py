#!/usr/bin/env python3
"""Pre-tool hook enforcing the `comment` and `pr-review` skill rules on GitHub posts.

Usage (hook JSON on stdin): check_gh_posts.py [claude|antigravity]

Always exits 0: only a JSON `deny` blocks a command. Anything that cannot be
parsed or read passes, because the hook enforces rules and is not a sandbox.
Standard library only.
"""
import json
import os
import re
import sys

WORD_CAP = 200
POSTING_COMMANDS = {("issue", "comment"), ("pr", "comment"), ("pr", "review")}
SHELL_PREFIX_WORDS = {"if", "then", "elif", "else", "do", "while", "until", "!", "{", "time", "command", "env", "nohup"}
VALUE_FLAGS = {"-R", "--repo", "--hostname"}


class Unparseable(ValueError):
    pass


# --- Shell reading -----------------------------------------------------------

class Word:
    def __init__(self, text, raw, dynamic):
        self.text = text          # value as far as it can be known
        self.raw = raw            # source spelling
        self.dynamic = dynamic    # part of the value is only known at run time


class Command:
    def __init__(self, piped_from):
        self.words = []
        self.heredoc = None
        self.herestring = None
        self.redirects = []       # (operator, Word)
        self.piped_from = piped_from


class ShellReader:
    """Splits a bash or PowerShell command line into simple commands."""

    def __init__(self, source, powershell):
        self.source = source.replace("\r\n", "\n")
        self.powershell = powershell
        self.escape = "`" if powershell else "\\"
        self.commands = []
        self.variables = {}
        self.position = 0

    def read(self):
        self._read_commands(nested=False)
        return self.commands

    def _peek(self, text):
        return self.source.startswith(text, self.position)

    def _read_commands(self, nested):
        """Reads until the end, or until the `)` closing a substitution."""
        first = len(self.commands)
        current, pending_heredocs, redirect, depth = Command(None), [], None, 0

        def finish(piped=False):
            nonlocal current
            previous = None
            if current.words or current.redirects or current.heredoc is not None:
                self._remember_assignment(current)
                self.commands.append(current)
                previous = current
            current = Command(previous if piped else None)

        while self.position < len(self.source):
            char = self.source[self.position]
            if char in " \t\r":
                self.position += 1
            elif self._peek(self.escape + "\n"):
                self.position += 2
            elif char == "\n":
                self.position += 1
                self._read_heredoc_bodies(pending_heredocs)
                # A pipe may continue on the next line.
                if current.words or current.piped_from is None:
                    finish()
            elif self.powershell and self._peek("<#"):
                end = self.source.find("#>", self.position)
                self.position = len(self.source) if end < 0 else end + 2
            elif char == "#":
                end = self.source.find("\n", self.position)
                self.position = len(self.source) if end < 0 else end
            elif self._peek("<<<"):
                self.position += 3
                redirect = "<<<"
            elif self._peek("<<"):
                self.position += 2
                pending_heredocs.append(self._read_heredoc_start(current))
            elif char in "<>" or self._peek("&>"):
                operator = re.compile(r"&>>?|>>|>&|>\||[<>]").match(self.source, self.position).group(0)
                self.position += len(operator)
                if current.words and current.words[-1].raw.isdigit() and self.source[self.position - len(operator) - 1].isdigit():
                    current.words.pop()
                redirect = operator
            elif self._peek("||") or self._peek("&&"):
                self.position += 2
                finish()
            elif char == "|":
                self.position += 1
                finish(piped=True)
            elif char in ";&":
                self.position += 1
                finish()
            elif char == "(":
                self.position += 1
                depth += 1
                finish()
            elif char == ")":
                self.position += 1
                if nested and depth == 0:
                    break
                depth -= 1
                finish()
            else:
                word = self._read_word()
                if redirect == "<<<":
                    current.herestring = word
                elif redirect:
                    current.redirects.append((redirect, word))
                else:
                    current.words.append(word)
                redirect = None
        else:
            if nested or pending_heredocs:
                raise Unparseable("unterminated substitution or heredoc")
        finish()
        return self.commands[first:]

    def _read_heredoc_start(self, command):
        match = re.compile(r"(-?)[ \t]*(?:'([^'\n]*)'|\"([^\"\n]*)\"|\\?([A-Za-z0-9_.-]+))").match(self.source, self.position)
        if not match:
            raise Unparseable("heredoc without delimiter")
        self.position = match.end()
        quoted = match.group(4) is None or "\\" in match.group(0)
        delimiter = next(group for group in match.group(2, 3, 4) if group is not None)
        return command, delimiter, bool(match.group(1)), quoted

    def _read_heredoc_bodies(self, pending):
        for command, delimiter, strip_tabs, quoted in pending:
            lines = []
            while True:
                if self.position >= len(self.source):
                    raise Unparseable("unterminated heredoc")
                end = self.source.find("\n", self.position)
                end = len(self.source) if end < 0 else end
                line = self.source[self.position:end]
                self.position = end + 1
                if strip_tabs:
                    line = line.lstrip("\t")
                if line == delimiter:
                    break
                lines.append(line)
            body = "\n".join(lines)
            command.heredoc = body if quoted else re.sub(r"\\([$`\\])", r"\1", body)
        pending.clear()

    def _read_word(self):
        start, parts, dynamic = self.position, [], False
        while self.position < len(self.source):
            char = self.source[self.position]
            following = self.source[self.position + 1:self.position + 2]
            if char in " \t\r\n;&|()<>":
                break
            if self.powershell and re.compile(r"@['\"][ \t]*\n").match(self.source, self.position):
                parts.append(self._read_here_string())
            elif char == "'":
                parts.append(self._read_single_quoted())
            elif char == '"':
                text, quoted_dynamic = self._read_double_quoted()
                parts.append(text)
                dynamic = dynamic or quoted_dynamic
            elif char == "$" and following == "'" and not self.powershell:
                parts.append(self._read_ansi_quoted())
            elif char == "$":
                text, expanded_dynamic = self._read_expansion()
                parts.append(text)
                dynamic = dynamic or expanded_dynamic
            elif char == self.escape:
                if following == "\n":
                    break
                # A backslash before an ordinary character stays, so Windows paths survive.
                if self.powershell or following in " \t'\"\\;&|()<>$`#":
                    parts.append(following)
                else:
                    parts.append(char + following)
                self.position += 2
            else:
                parts.append(char)
                self.position += 1
        if self.position == start:
            raise Unparseable("unreadable shell text")
        return Word("".join(parts), self.source[start:self.position], dynamic)

    def _read_here_string(self):
        quote = self.source[self.position + 1]
        begin = self.source.index("\n", self.position) + 1
        end = self.source.find("\n" + quote + "@", begin - 1)
        if end < 0:
            raise Unparseable("unterminated here-string")
        self.position = end + 3
        return self.source[begin:end] if end >= begin else ""

    def _read_single_quoted(self):
        parts = []
        self.position += 1
        while True:
            end = self.source.find("'", self.position)
            if end < 0:
                raise Unparseable("unterminated quote")
            parts.append(self.source[self.position:end])
            self.position = end + 1
            if not (self.powershell and self._peek("'")):
                return "".join(parts)
            parts.append("'")
            self.position += 1

    def _read_ansi_quoted(self):
        match = re.compile(r"\$'((?:\\.|[^'\\])*)'", re.S).match(self.source, self.position)
        if not match:
            raise Unparseable("unterminated quote")
        self.position = match.end()
        escapes = {"n": "\n", "t": "\t", "r": ""}
        return re.sub(r"\\(.)", lambda found: escapes.get(found.group(1), found.group(1)), match.group(1))

    def _read_double_quoted(self):
        parts, dynamic = [], False
        self.position += 1
        while self.position < len(self.source):
            char = self.source[self.position]
            following = self.source[self.position + 1:self.position + 2]
            if char == '"':
                self.position += 1
                if self.powershell and self._peek('"'):
                    parts.append('"')
                    self.position += 1
                    continue
                return "".join(parts), dynamic
            if char == self.escape and following:
                if self.powershell:
                    parts.append({"n": "\n", "t": "\t", "r": ""}.get(following, following))
                elif following in "$`\"\\":
                    parts.append(following)
                elif following != "\n":
                    parts.append(char + following)
                self.position += 2
            elif char == "$":
                text, expanded_dynamic = self._read_expansion()
                parts.append(text)
                dynamic = dynamic or expanded_dynamic
            else:
                parts.append(char)
                self.position += 1
        raise Unparseable("unterminated quote")

    def _read_expansion(self):
        if self._peek("$("):
            self.position += 2
            inner = self._read_commands(nested=True)
            # `$(cat <<'EOF' ... EOF)` is the usual way to pass a multi-line body.
            if len(inner) == 1 and [word.text for word in inner[0].words] == ["cat"] and inner[0].heredoc is not None:
                return inner[0].heredoc.rstrip("\n"), False
            return "", True
        match = re.compile(r"\$(?:\{([^}\n]*)\}|([A-Za-z_][A-Za-z0-9_]*(?::[A-Za-z_][A-Za-z0-9_]*)?))").match(self.source, self.position)
        if not match:
            self.position += 1
            return "$", False
        self.position = match.end()
        name = match.group(1) or match.group(2)
        if name in self.variables:
            return self.variables[name], False
        return "", True

    def _remember_assignment(self, command):
        words = command.words
        if self.powershell and len(words) == 3 and words[1].raw == "=" and words[0].raw.startswith("$"):
            name, value = words[0].raw[1:], words[2]
        elif len(words) == 1 and re.match(r"[A-Za-z_][A-Za-z0-9_]*=", words[0].raw):
            name, text = words[0].text.split("=", 1)
            value = Word(text, "", words[0].dynamic)
        else:
            return
        if value.dynamic:
            self.variables.pop(name, None)
        else:
            self.variables[name] = value.text


# --- Finding the posts -------------------------------------------------------

class Post:
    def __init__(self, kind, approve, bodies):
        self.kind = kind          # ("issue"|"pr", "comment"|"review")
        self.approve = approve
        self.bodies = bodies


def program_words(command):
    words = list(command.words)
    while words and (words[0].text in SHELL_PREFIX_WORDS or re.match(r"[A-Za-z_][A-Za-z0-9_]*=", words[0].raw)):
        words.pop(0)
    return words


def program_name(words):
    if not words:
        return ""
    name = re.split(r"[/\\]", words[0].text)[-1].lower()
    return name[:-4] if name.endswith(".exe") else name


class Workspace:
    """The files a body can come from, as they will be when the command runs."""

    def __init__(self, cwd):
        self.cwd = cwd
        self.written = {}         # path -> text written earlier in this command, or None if unknown

    def resolve(self, word):
        if word.dynamic or not word.text or self.cwd is None and not os.path.isabs(word.text):
            return None
        path = os.path.expanduser(word.text)
        return os.path.normpath(path if os.path.isabs(path) else os.path.join(self.cwd, path))

    def read(self, word):
        path = self.resolve(word)
        if path is None:
            return None
        if path in self.written:
            return self.written[path]
        try:
            with open(path, "rb") as stream:
                return stream.read().decode("utf-8-sig", "replace")
        except OSError:
            return None

    def track(self, command):
        words = program_words(command)
        name = program_name(words)
        arguments = [word for word in words[1:] if not word.text.startswith("-")]
        if name in ("cd", "set-location", "pushd") and arguments:
            self.cwd = self.resolve(arguments[0])
        for operator, target in command.redirects:
            if operator.startswith("<") or operator == ">&":
                continue
            known = command.heredoc if name == "cat" and len(words) == 1 and operator in (">", ">|") else None
            self._mark_written(target, known)
        if name in ("tee", "set-content", "out-file", "add-content", "cp", "mv", "copy-item", "move-item"):
            for argument in arguments:
                self._mark_written(argument, None)

    def _mark_written(self, target, text):
        path = self.resolve(target)
        if path is not None:
            self.written[path] = text


def piped_text(command, workspace):
    """The text arriving on a command's stdin, when it can be known."""
    if command.heredoc is not None:
        return command.heredoc
    if command.herestring is not None:
        return command.herestring.text
    for operator, target in command.redirects:
        if operator == "<":
            return workspace.read(target)
    source = command.piped_from
    if source is None:
        return None
    words = program_words(source)
    name = program_name(words)
    if name == "cat" and len(words) == 2:
        return workspace.read(words[1])
    if name == "cat" and len(words) == 1:
        return source.heredoc
    if len(words) == 1 and words[0].raw[:1] in ("$", "@", "'", '"'):
        return words[0].text
    return None


def parse_gh(command, workspace):
    words = program_words(command)
    if program_name(words) != "gh":
        return None
    positional, flags, index = [], [], 1
    while index < len(words):
        text = words[index].text
        if text.startswith("-") and len(text) > 1:
            if text in VALUE_FLAGS:
                index += 1
            elif text.startswith("--"):
                name, has_value, value = text.partition("=")
                if name in ("--body", "--body-file"):
                    if not has_value:
                        index += 1
                        flags.append((name, words[index] if index < len(words) else None))
                    else:
                        flags.append((name, Word(value, value, words[index].dynamic)))
                elif name == "--approve" and value != "false":
                    flags.append((name, None))
            else:
                index = parse_short_flags(words, index, flags)
        else:
            positional.append(text)
        index += 1
    kind = tuple(positional[:2])
    if kind not in POSTING_COMMANDS:
        return None
    return Post(kind, kind == ("pr", "review") and any(name == "--approve" for name, _ in flags), bodies_of(flags, command, workspace))


def parse_short_flags(words, index, flags):
    text = words[index].text
    for offset, letter in enumerate(text[1:], 1):
        if letter == "a":
            flags.append(("--approve", None))
        elif letter in "bFR":
            name = {"b": "--body", "F": "--body-file", "R": "--repo"}[letter]
            value = text[offset + 1:].lstrip("=")
            if value:
                flags.append((name, Word(value, value, words[index].dynamic)))
            else:
                index += 1
                flags.append((name, words[index] if index < len(words) else None))
            break
    return index


def bodies_of(flags, command, workspace):
    bodies = []
    for name, value in flags:
        if value is None:
            continue
        if name == "--body":
            bodies.append(value.text)
        elif name == "--body-file":
            text = piped_text(command, workspace) if value.text == "-" else workspace.read(value)
            if text is not None:
                bodies.append(text)
    return bodies


def find_posts(command_line, cwd, powershell):
    workspace = Workspace(cwd)
    posts = []
    for command in ShellReader(command_line, powershell).read():
        post = parse_gh(command, workspace)
        if post:
            posts.append(post)
        workspace.track(command)
    return posts


# --- Rules -------------------------------------------------------------------

FENCE = re.compile(r"^[ \t>]*(`{3,}|~{3,})[ \t]*([^`\n]*)$")
OUTPUT_LANGUAGES = {"console", "shell-session", "sh-session", "terminal", "output", "log"}
UNTYPED_LANGUAGES = {"", "text", "txt", "plaintext", "bash", "sh", "shell", "powershell", "pwsh", "ps1"}
# A script line that only talks about a result: a comment or a print statement.
NOT_SCRIPT_TALK = r"^(?![ \t]*(?:#|echo\b|printf\b|Write-Host\b|Write-Output\b)).*?"
# Each entry matches the wording a tool prints, never a statement a script contains.
OUTPUT_SIGNS = re.compile("|".join((
    r"^\s*\$ \S",
    r"^\s*PS [A-Z]:\\[^>]*> ",
    r"^Ran \d+ tests? in ",
    r"^OK( \(.*\))?$",
    r"^FAILED($| \(|:| \S+::)",
    r"^(PASS|FAIL|PASSED|ERROR)\b(?![ \t]*[=\"'$(])[ \t:]",
    r"^(not )?ok \d+\b",
    r"^ok[ \t]+\S+[ \t]+(\(cached\)|[\d.]+s\b)",
    r"^\s*\[(PASS|FAIL|ERROR|OK|WARN)\]",
    r"^\s*(---|===) (PASS|FAIL|RUN)\b",
    NOT_SCRIPT_TALK + r"\b\d+ (passed|failed|passing|failing)\b",
    r"^\s*(Tests?|Test Suites|Results):\s+\d+",
    r"^Traceback \(most recent call last\)",
    r"^npm (ERR!|error) ",
    NOT_SCRIPT_TALK + r"\b(?:[Ee]xit(?:ed with)? (?:code|status)|[Ee]xited with)[ :=]+\d+\b",
    r"^(\[[A-Z]+\] )?BUILD (SUCCESS|FAILURE|FAILED)",
    r"^(Preflight|Outcome): (PASS|FAIL|BLOCKED)",
    r"\berror TS\d+:",
    r"^(fatal|error): ",
    r"^On branch \S",
)), re.M)
CHECK_ROW = re.compile("|".join((
    r"^.+?(\t| {2,})(pass|fail|pending|skipping|cancel)(\t| {2,}|\s*$)",
    r"^[✓✔X✗×*○◦-]\s+\S",
    r"^(All|Some) checks\b",
    r"^\d+ (cancelled|failing|successful|skipped|pending)\b",
    r"^NAME\s+",
    r"^\$ gh pr checks\b",
    r"^no checks reported\b",
)))
CHECK_STATE = re.compile(r"(\t| {2,})(pass|fail|pending|skipping|cancel)(\t| {2,}|\s*$)|^(All|Some) checks\b|^no checks reported\b", re.M)


def split_fences(body):
    """Returns the prose outside fenced blocks and each (language, content) block."""
    prose, blocks, fence, content, language = [], [], None, [], ""
    for line in body.replace("\r\n", "\n").split("\n"):
        match = FENCE.match(line)
        if fence is None and match:
            fence, content = match.group(1), []
            language = (match.group(2).split() or [""])[0].lower()
        elif fence is not None and match and match.group(1).startswith(fence) and not match.group(2).strip():
            blocks.append((language, "\n".join(content)))
            fence = None
        elif fence is None:
            prose.append(line)
        else:
            content.append(re.sub(r"^\s*> ?", "", line))
    if fence is not None:
        blocks.append((language, "\n".join(content)))
    return "\n".join(prose), blocks


def is_checks_table(content):
    lines = [line for line in content.split("\n") if line.strip()]
    return bool(CHECK_STATE.search(content)) and all(CHECK_ROW.match(line) for line in lines)


def looks_like_output(language, content):
    if language in OUTPUT_LANGUAGES:
        return True
    if language not in UNTYPED_LANGUAGES:
        return False
    return bool(OUTPUT_SIGNS.search(content)) or is_checks_table(content)


def without_code_and_links(prose):
    prose = re.sub(r"<!--.*?-->", " ", prose, flags=re.S)
    prose = re.sub(r"(?<!`)(`+)(?!`)(?:(?!\n[ \t]*\n).)+?(?<!`)\1(?!`)", " ", prose, flags=re.S)
    return re.sub(r"https?://[^\s)>\]]+", " ", prose)


def blocking_violations(post, body):
    prose, blocks = split_fences(body)
    visible = without_code_and_links(prose)
    found = []
    mentions = sorted(set(re.findall(r"(?<![\w.+/@\\-])@[A-Za-z0-9][A-Za-z0-9-]*", visible)))
    if mentions:
        found.append("`@name` outside code (%s): it notifies a real account. Write the role without `@`, or put the text in backticks." % ", ".join(mentions[:5]))
    numbers = sorted(set(re.findall(r"(?<![\w/&\\])#\d+\b", visible)))
    if numbers:
        found.append("bare `#N` outside code (%s): it cross-links another issue or PR. Use `ST-XXXXXX` or plain text." % ", ".join(numbers[:5]))
    for language, content in blocks:
        if post.kind[0] == "pr" and is_checks_table(content):
            continue
        if looks_like_output(language, content):
            found.append("fenced block that looks like command or test output: cite what was checked and a one-line result instead. Only the `gh pr checks` table is allowed, and only in PR comments.")
            break
    return found


def warnings_for(post, body):
    prose, blocks = split_fences(body)
    found = []
    pasted_checks = sum(len(content.split()) for _, content in blocks if post.kind[0] == "pr" and is_checks_table(content))
    count = len(body.split()) - pasted_checks
    stated = any(re.search(r"\bexempt|\bexception\b", line, re.I) and re.search(r"words?\b|\bcap\b|\b200\b|\blength\b|by exception", line, re.I)
                 for line in prose.split("\n"))
    if count > WORD_CAP and not stated:
        found.append("about %d words (cap about %d) with no stated exception: cut it, or state the exemption in the comment." % (count, WORD_CAP))
    visible = without_code_and_links(prose)
    if "**Thread Status:**" in visible and not re.search(r"\*\*Decision\b[^*\n]*\*\*", visible):
        found.append("`**Thread Status:**` without `**Decision:**`.")
    return found


def evaluate(posts):
    denials, warnings = [], []
    for post in posts:
        if post.approve:
            denials.append("`gh pr review --approve` is not allowed: GitHub blocks self-approval. Post the verdict with `gh pr comment`.")
        for body in post.bodies:
            denials += blocking_violations(post, body)
            warnings += warnings_for(post, body)
    return list(dict.fromkeys(denials)), list(dict.fromkeys(warnings))


# --- Provider adapter --------------------------------------------------------

def read_request(provider, payload):
    """Returns (command line, working directory, is PowerShell)."""
    if provider == "antigravity":
        arguments = payload["toolCall"]["args"]
        command, cwd, powershell = arguments["CommandLine"], arguments.get("Cwd"), os.name == "nt"
    else:
        command, cwd = payload["tool_input"]["command"], payload.get("cwd")
        powershell = payload.get("tool_name") == "PowerShell"
    if not isinstance(command, str):
        raise Unparseable("no command text")
    # Only PowerShell has these here-strings, whatever the tool is called.
    return command, cwd, powershell or bool(re.search(r"@['\"][ \t]*\r?\n", command))


def reply(provider, denials, warnings):
    """The provider's JSON answer, or None when saying nothing means pass."""
    reason = ""
    if denials:
        reason = "Blocked by check_gh_posts (rules: `comment` skill):\n" + "\n".join("- " + item for item in denials)
    if warnings:
        reason += ("\n" if reason else "") + "check_gh_posts warning:\n" + "\n".join("- " + item for item in warnings)
    if provider == "antigravity":
        answer = {"decision": "deny" if denials else "allow"}
        if reason:
            answer["reason"] = reason
        return answer
    if not reason:
        return None
    output = {"hookEventName": "PreToolUse"}
    if denials:
        output.update(permissionDecision="deny", permissionDecisionReason=reason)
    else:
        output["additionalContext"] = reason
    return {"hookSpecificOutput": output}


def respond(provider, raw):
    denials, warnings = [], []
    try:
        payload = json.loads(raw)
        provider = provider or ("antigravity" if "toolCall" in payload else "claude")
        command, cwd, powershell = read_request(provider, payload)
        if "gh" in command:
            denials, warnings = evaluate(find_posts(command, cwd or os.getcwd(), powershell))
    except Exception:  # fail open: a hook defect must never stop shell commands
        denials, warnings = [], []
    return reply(provider, denials, warnings)


def main(argv):
    provider = argv[0] if argv and argv[0] in ("claude", "antigravity") else None
    answer = respond(provider, sys.stdin.buffer.read().decode("utf-8", "replace"))
    if answer is not None:
        print(json.dumps(answer))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
