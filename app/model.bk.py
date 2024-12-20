class OperadorAgenteCRUDSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Inclui o serializer do User para manipular dados do usuário

    class Meta:
        model = Agente
        fields = ['id', 'user', 'empresa', 'numero_telefone', 'endereco']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        agente = Agente.objects.create(user=user, **validated_data)
        return agente

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        user = instance.user

        if user_data:
            # Atualiza o usuário relacionado
            user_serializer = UserSerializer(instance=user, data=user_data, partial=True)
            if user_serializer.is_valid():
                user_serializer.save()
            else:
                raise serializers.ValidationError(user_serializer.errors)

        # Atualiza dados do agente
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
