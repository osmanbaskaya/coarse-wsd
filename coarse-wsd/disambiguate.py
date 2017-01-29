from ims import predict
import utils


if __name__ == '__main__':
    utils.configure_logger()
    model_dir = '../datasets/models/'
    input_dir = '/tmp/ims-mt-dataset/'
    output_dir = '/tmp/ims-outputs/'
    predict(model_dir, input_dir, output_dir, num_of_process=7)

