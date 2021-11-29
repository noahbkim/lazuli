from starlette.applications import Starlette

from .machinery import Endpoint

from typing import Callable, Union, Type


class Lazuli(Starlette):
    """Root application endpoints are registered to."""

    def add_endpoint(
            self,
            path: str,
            endpoint: Endpoint,
            name: str,
            include_in_schema: bool = True):
        """Add an endpoint to the app."""

        endpoint.add(self, path, name, include_in_schema=include_in_schema)

    def endpoint(
            self,
            path: str,
            name: str = None,
            include_in_schema: bool = True) -> Callable[[Endpoint], None]:
        """Provide a registration decorator."""

        def decorator(endpoint: Union[Endpoint, Type[Endpoint]]):
            if isinstance(endpoint, type):
                endpoint = endpoint()
            self.add_endpoint(path, endpoint, name, include_in_schema=include_in_schema)

        return decorator
