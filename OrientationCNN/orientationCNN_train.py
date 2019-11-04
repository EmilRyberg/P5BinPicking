import tensorflow as tf

def create_model():
    input_tensor = tf.keras.layers.Input(shape=(224, 224, 3))
    vgg_model = tf.keras.applications.vgg16.VGG16(include_top=False, input_tensor=input_tensor)
    #for l in model.layers:
    #    print(l.name, l.trainable)

    for i in range(10):
        print(f"Locking layer {i}")
        vgg_model.layers[i].trainable = False

    X = tf.keras.layers.Flatten()(vgg_model.output)
    X = tf.keras.layers.Dense(512, activation="relu")(X)
    X = tf.keras.layers.Dense(512, activation="relu")(X)
    X = tf.keras.layers.Dense(1, activation="sigmoid")(X)

    model = tf.keras.models.Model(inputs=input_tensor, outputs=X)

    print(model.summary())

    return model


if __name__ == "__main__":
    model = create_model()
    datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
    train_generator = datagen.flow_from_directory("OrientationCNN/dataset/train", target_size=(224, 224), batch_size=1, class_mode="binary")
    test_generator = datagen.flow_from_directory("OrientationCNN/dataset/test", target_size=(224, 224), batch_size=1, class_mode="binary")
    model.compile("adam", loss="binary_crossentropy", metrics=["accuracy"])
    model.fit_generator(train_generator, steps_per_epoch=500, epochs=2, validation_data=test_generator, validation_steps=500)