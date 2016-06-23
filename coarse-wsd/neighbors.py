import sys
from representation import load_model


def run():
    model_id = sys.argv[1]
    keydict_path = sys.argv[2]
    words = sys.argv[3:]
    model = load_model(model_id)
    print model



if __name__ == '__main__':
    run()
