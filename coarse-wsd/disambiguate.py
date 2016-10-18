from ims import IMSPredictor


if __name__ == '__main__':
    model_dir = '../datasets/ims-run/fold-1'
    test_xml = '../datasets/ims/fold-1/chair.train.xml'
    target_word = 'chair'
    predictor = IMSPredictor(model_dir)
    predictor.transform(target_word, test_xml)
