from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import (
    ContentType,
    GenericForeignKey,
    GenericRelation,
)

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from utils.models import BaseModel


User = get_user_model()


class Message(BaseModel):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages_sent"
    )
    reciever = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages_received"
    )

    # content = models.TextField()

    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to={"model__in": ("text", "video", "image", "file", "audio")},
        on_delete=models.CASCADE,
    )

    is_read = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.sender_id} - {self.reciever_id}"

    def notify_ws_clients(self):
        """
        Inform client there is a new message.
        """
        notification = {
            "type": "recieve_group_message",
            "message": "{}".format(self.id),
        }

        channel_layer = get_channel_layer()
        print("sender.id {}".format(self.sender_id))
        print("reciever.id {}".format(self.reciever_id))

        async_to_sync(channel_layer.group_send)("{}".format(self.user.id), notification)
        async_to_sync(channel_layer.group_send)(
            "{}".format(self.recipient.id), notification
        )

    def save(self, *args, **kwargs):
        """
        Trims white spaces, saves the message and notifies the recipient via WS
        if the message is new.
        """
        new = self.id
        self.body = self.body.strip()
        super().save(*args, **kwargs)
        if new is None:
            self.notify_ws_clients()


class ObjectBase(models.Model):
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="%(class)s_related"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Text(ObjectBase):
    content = models.TextField()


class Audio(ObjectBase):
    content = models.FileField(upload_to="audio")


class Image(ObjectBase):
    content = models.ImageField(upload_to="images")


class File(ObjectBase):
    content = models.FileField(upload_to="file")


class Chat(BaseModel):
    user1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owner_chats"
    )
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats")

    class Meta:
        unique_together = ("user1", "user2")
