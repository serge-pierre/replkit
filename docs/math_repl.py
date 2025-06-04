from replkit import repl

class MathInterpreter:
  def eval(self, line):
    try:
      result = eval(line, {}, {})
      print(result)
    except Exception as e:
      print("Error:", e)
  def get_keywords(self):
    return {"+", "-", "*", "/", "exit"}
  
if __name__ == "__main__":
  repl(interpreter=MathInterpreter(), argv=["--file", "init.txt", "--run", "1+2", "--prompt", "Math> ", "--loglevel", "debug", "--hello", "Welcome in MathInterpreter"])