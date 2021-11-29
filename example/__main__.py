from lazuli.machinery import CollectionEndpoint
from lazuli.bounds import Request, Response
from lazuli import Lazuli

application = Lazuli(debug=True)


class User:
    """A simple model."""

    email: str
    password: str
    first_name: str
    last_name: str


@application.endpoint(path="/users/", name="users")
class UserEndpoint(CollectionEndpoint):
    """Displays users."""

    model = User

    def create(self, request: Request) -> Response:
        return Response(content={"data": {"id": "1", "type": "users"}})
