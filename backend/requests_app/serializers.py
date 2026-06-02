"""Serializers de validación para las solicitudes de material."""
from rest_framework import serializers

from .catalog import material_ids, store_names


class MaterialItemSerializer(serializers.Serializer):
    material = serializers.CharField()
    units = serializers.IntegerField(min_value=1)

    def validate_material(self, value):
        if value not in material_ids():
            raise serializers.ValidationError(
                f"Material no válido: '{value}'."
            )
        return value


class MaterialRequestSerializer(serializers.Serializer):
    store = serializers.CharField()
    requester = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
    reason = serializers.CharField()
    items = MaterialItemSerializer(many=True)

    def validate_store(self, value):
        if value not in store_names():
            raise serializers.ValidationError(
                f"Tienda no válida: '{value}'."
            )
        return value

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "Debes añadir al menos un material."
            )
        return value
