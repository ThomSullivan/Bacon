from rest_framework import permissions
from forum.models import Comment

class IsCommentOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        comment = Comment.objects.filter(owner=request.user)
        try:
            if request.user == comment[0].owner:
                return True
        except:
            return False
        
        
            