from ims import IMSPredictor


if __name__ == '__main__':
    model_dir = '../datasets/models/'
    test_xml = '/tmp/ims-mt-dataset/ability.xml'
    target_word = 'ability'
    predictor = IMSPredictor(model_dir)
    predictor.transform(target_word, test_xml)
