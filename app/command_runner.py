import os
import subprocess

MAX_OUTPUT_LENGTH = 3500
COMMAND_TIMEOUT = 30

current_working_dir = os.getcwd()

def run_command(command: str) -> str:
    global current_working_dir

    cmd_stripped = command.strip()

    if cmd_stripped == "cd" or cmd_stripped.startswith("cd "):
        target_dir = cmd_stripped[3:].strip()

        if not target_dir or target_dir == "~":
            target_dir = os.path.expanduser("~")

        try:
            new_dir = os.path.abspath(os.path.join(current_working_dir, target_dir))

            if os.path.isdir(new_dir):
                current_working_dir = new_dir
                return f"Changed directory to:\n{current_working_dir}"
            else:
                return f"cd: {target_dir}: No such file or directory"
        except Exception as e:
            return f"Error changing directory: {str(e)}"

    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=current_working_dir,
            capture_output=True,
            text=True,
            timeout=COMMAND_TIMEOUT
        )

        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"

        if not output.strip():
            return "Command executed successfully with no output"
        
        if len(output) > MAX_OUTPUT_LENGTH:
            output = output[:MAX_OUTPUT_LENGTH] + "\n...[OUTPUT TRUNCATED]"

        return output
    except subprocess.TimeoutExpired:
        return f"Command timed out after {COMMAND_TIMEOUT} seconds."
    except Exception as e:
        return f"Error executig command: {str(e)}"