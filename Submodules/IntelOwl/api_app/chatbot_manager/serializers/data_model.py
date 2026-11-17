# This file is a part of IntelOwl https://github.com/intelowlproject/IntelOwl
# See the file 'LICENSE' for copying permission.

from rest_framework import serializers

from .base import ToolResultSerializer


class DataModelResultSerializer(ToolResultSerializer):
    # `data_model` is already produced by the model's own DRF serializer
    # (`BaseDataModel.serialize()`, polymorphic across Domain/IP/File), so the envelope
    # just carries that dict (empty `{}` when the job has no data model).
    data_model = serializers.DictField(read_only=True)
