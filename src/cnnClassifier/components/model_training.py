import os
import urllib.request as request
from pathlib import Path
from zipfile import ZipFile
import tensorflow as tf
import time
from keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

from src.cnnClassifier.entity.config_entity import TrainingConfig


class Training:
    def __init__(self, config: TrainingConfig):
        self.config = config

    def get_base_model(self):
        self.model = tf.keras.models.load_model(
            self.config.updated_base_model_path,
        )

    def train_valid_generator(self):

        datagenerator_kwargs = dict(
            rescale=1. / 255,
            validation_split=0.2,
        )

        dataflow_kwargs = dict(
            target_size=self.config.params_image_size[:-1],
            batch_size=self.config.params_batch_size,
            interpolation="bilinear",
        )

        valid_datagenerator = tf.keras.preprocessing.image.ImageDataGenerator(
            **datagenerator_kwargs
        )

        self.valid_generator = valid_datagenerator.flow_from_directory(
            directory=self.config.training_data,
            subset="validation",
            shuffle=False,
            **dataflow_kwargs
        )

        if self.config.params_is_augmentation:
            train_datagenerator = tf.keras.preprocessing.image.ImageDataGenerator(
                rotation_range=40,
                horizontal_flip=True,
                width_shift_range=0.2,
                height_shift_range=0.2,
                shear_range=0.2,
                zoom_range=0.2,
                **datagenerator_kwargs
            )
        else:
            train_datagenerator = valid_datagenerator

        self.train_generator = train_datagenerator.flow_from_directory(
            directory=self.config.training_data,
            subset="training",
            shuffle=True,
            **dataflow_kwargs
        )

    @staticmethod
    def save_model(path: Path, model: tf.keras.Model):
        model.save(path)

    def train(self):
        self.steps_per_epoch = self.train_generator.samples // self.train_generator.batch_size
        self.validation_steps = self.valid_generator.samples // self.valid_generator.batch_size

        callbacks = [
            ModelCheckpoint(self.config.updated_base_model_path, verbose=1, save_best_only=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.1, patience=3, verbose=1, min_lr=1e-6),
            EarlyStopping(monitor='val_loss', patience=7, verbose=1),
        ]

        self.model.fit(
            self.train_generator,
            steps_per_epoch=self.steps_per_epoch,
            epochs=self.config.params_epochs,
            validation_data=self.valid_generator,
            validation_steps=self.validation_steps,
            callbacks=[callbacks],
        )

        self.save_model(path=self.config.trained_model_path, model=self.model)
        self.save_model(path=self.config.cloud_model_path, model=self.model)
