import os
import shutil

def pytest_assertrepr_compare(config, op, left, right):
    error_line = f"{left} {op} {right}"
    test_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0].replace('[', '_').replace(']', '_')
    log_path = "/tmp/logs/output_test.log"
    log_path_new = f"/tmp/logs/output_{test_name}.log"
    if os.path.exists(log_path_new):
        os.remove(log_path_new)
    if os.path.exists(log_path):
        shutil.copyfile(log_path, log_path_new)
        log_line = f"(View logs here: file://{log_path_new})"
    else:
        log_line = f"Logs not found"
    return [error_line, log_line]