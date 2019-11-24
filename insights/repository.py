def create(obj):
    obj.save()
    return obj


def delete(obj):
    obj.delete()
