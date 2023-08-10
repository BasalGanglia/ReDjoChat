from django.shortcuts import render
from rest_framework import viewsets
from .serializer import ServerSerializer
from .models import Server
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from django.db.models import Count
from .schema import server_list_docs

"""
A viewset for listing servers.

Allows for filtering servers based on query parameters such as category, quantity, user, server ID,
and the presence of member count.

Attributes
----------
queryset : QuerySet
    A queryset containing all Server objects.

Methods
-------
list(request)
    Returns a list of servers based on the query parameters.


    The list can be filtered by:
    - `category`: Filter servers by category name.
    - `qty`: Limit the number of servers in the response.
    - `by_user`: Filter servers by a specific user (requires authentication).
    - `by_serverid`: Filter by a specific server ID.
    - `with_num_members`: If true, annotate servers with the number of members.

    Parameters
    ----------
    request : Request
        The HTTP request object containing query parameters for filtering.

    Returns
    -------
    Response
        A response object containing a list of serialized Server objects.

    Raises
    ------
    AuthenticationFailed
        If trying to filter by user or server ID without being authenticated.
    ValidationError
        If an invalid server ID is provided or if a server is not found by ID.
"""


class ServerListViewSet(viewsets.ViewSet):
    queryset = Server.objects.all()

    @server_list_docs
    def list(self, request):
        """
        Returns a list of servers based on the query parameters.

        The list can be filtered by:
        - `category`: Filter servers by category name.
        - `qty`: Limit the number of servers in the response.
        - `by_user`: Filter servers by a specific user (requires authentication).
        - `by_serverid`: Filter by a specific server ID.
        - `with_num_members`: If true, annotate servers with the number of members.

        Parameters
        ----------
        request : Request
            The HTTP request object containing query parameters for filtering.

        Returns
        -------
        Response
            A response object containing a list of serialized Server objects.

        Raises
        ------
        AuthenticationFailed
            If trying to filter by user or server ID without being authenticated.
        ValidationError
            If an invalid server ID is provided or if a server is not found by ID.
        """

        category = request.query_params.get("category", None)
        qty = request.query_params.get("qty", None)
        by_user = request.query_params.get("by_user") == "true"
        by_serverid = request.query_params.get("by_serverid", None)
        with_num_members = request.query_params.get("with_num_members") == "True"

        if by_user or by_serverid and not request.user.is_authenticated:
            raise AuthenticationFailed("You must be logged in to perform this action")

        if category is not None:
            self.queryset = self.queryset.filter(category__name=category)

        if qty is not None:
            self.queryset = self.queryset[: int(qty)]

        if by_user:
            user_id = request.user.id
            self.queryset = self.queryset.filter(member=user_id)

        if with_num_members:
            self.queryset = self.queryset.annotate(num_members=Count("member"))

        if by_serverid is not None:
            try:
                self.queryset = self.queryset.filter(id=int(by_serverid))
                if not self.queryset.exists():
                    raise ValidationError("Server not found")
            except ValueError:
                raise ValidationError("Invalid server id")

        serializer = ServerSerializer(
            self.queryset, many=True, context={"num_members": with_num_members}
        )
        return Response(serializer.data)


# class ServerListViewSet(viewsets.ViewSet):
#     """
#     A viewset for listing servers.

#     ...

#     Attributes
#     ----------
#     queryset : QuerySet
#         A queryset containing all Server objects.

#     Methods
#     -------
#     list(request)
#         Returns a list of servers based on the query parameters.
#     """

#     queryset = Server.objects.all()

#     def list(self, request):
#         """
#         Returns a list of servers based on the query parameters.

#         Parameters
#         ----------
#         request : Request
#             The HTTP request object.

#         Returns
#         -------
#         Response
#             A response object containing a list of serialized Server objects.
#         """

#         category = request.query_params.get("category", None)
#         qty = request.query_params.get("qty", None)
#         by_user = request.query_params.get("by_user") == "true"
#         by_serverid = request.query_params.get("by_serverid", None)
#         with_num_members = request.query_params.get("with_num_members") == "True"

#         if by_user or by_serverid and not request.user.is_authenticated:
#             raise AuthenticationFailed("You must be logged in to perform this action")

#         if category is not None:
#             self.queryset = self.queryset.filter(category__name=category)

#         if qty is not None:
#             self.queryset = self.queryset[: int(qty)]

#         if by_user:
#             user_id = request.user.id
#             self.queryset = self.queryset.filter(member=user_id)

#         if with_num_members:
#             self.queryset = self.queryset.annotate(num_members=Count("member"))

#         if by_serverid is not None:
#             try:
#                 self.queryset = self.queryset.filter(id=int(by_serverid))
#                 if not self.queryset.exists():
#                     raise ValidationError("Server not found")
#             except ValueError:
#                 raise ValidationError("Invalid server id")

#         serializer = ServerSerializer(
#             self.queryset, many=True, context={"num_members": with_num_members}
#         )
#         return Response(serializer.data)
