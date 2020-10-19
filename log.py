class Log:
    def __init__(self, log_path: str):
        self.log_path = log_path
        self.stdout = True
        file = open(log_path, "w")
        file.close()

    def log(self, message: str):
        file = open(self.log_path, "a")
        file.write(message + "\n")
        file.close()
        if self.stdout:
            print(message)

    def stdout(self, stdout):
        self.stdout = stdout
