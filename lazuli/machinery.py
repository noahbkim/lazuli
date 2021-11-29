from starlette.applications import Starlette
from starlette.routing import Route

from typing import List, Callable, Optional, Type, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass

from .bounds import Request, Response


@dataclass
class Handler:
    """Type for request handler."""

    method: Callable[[...], None]
    parent_hint: Optional[List[type]]
    nested_hint: int

    def __get__(self, endpoint: "Endpoint", endpoint_type: Type["Endpoint"] = None):
        """Get the underlying method."""

        return self.method


class HandlerRegistrar:
    ...


class Endpoint(ABC):
    """Combination of a view and a router."""

    children: List["Endpoint"]
    handlers: List["Handler"]

    def __init__(self):
        """Initialize a new endpoint."""

        self.children = []

    @abstractmethod
    def add(
            self,
            application: Starlette,
            path: str,
            name: str,
            include_in_schema: bool = True):
        """Return a list of routes to register."""


class CollectionEndpoint(Endpoint):
    """Provides collection and individual views."""

    parameter: str

    def __init__(self, parameter: str):
        """Set the parameter name of the item wildcard."""

        super().__init__()
        self.parameter = parameter

    @abstractmethod
    def create(self, request: Request) -> Response:
        """Create a new item."""

    @abstractmethod
    def list(self, request: Request) -> Response:
        """Get a list of items based on the query."""

    @abstractmethod
    def retrieve(self, request: Request, identifier: str) -> Response:
        """Retrieve a single item."""

    @abstractmethod
    def update(self, request: Request, identifier: str) -> Response:
        """Update a single item."""

    @abstractmethod
    def delete(self, request: Request, identifier: str) -> Response:
        """Delete a single item."""

    def handle_collection(self, request: Request) -> Response:
        """Dispatch create, list."""

        if request.method == "POST":
            return self.create(request)
        elif request.method == "GET":
            return self.list(request)
        raise RuntimeError(f"unexpected method: {request.method}")

    def handle_item(self, request: Request) -> Response:
        """Dispatch retrieve, update, delete."""

        if request.method == "GET":
            return self.retrieve(request, request.path_params[self.parameter])
        elif request.method == "PATCH":
            return self.update(request, request.path_params[self.parameter])
        elif request.method == "DELETE":
            return self.delete(request, request.path_params[self.parameter])
        raise RuntimeError(f"unexpected method: {request.method}")

    def add(
            self,
            application: Starlette,
            path: str,
            name: str,
            include_in_schema: bool = True):
        """Return a list of routes to register."""

        application.add_route(
            path=path,
            route=self.handle_collection,
            methods=["GET", "POST"],
            name=f"{name}_collection" if name is not None else None,
            include_in_schema=include_in_schema)
        application.add_route(
            path=f"""{path.rstrip("/")}/{{{self.parameter}}}""",
            route=self.handle_item,
            methods=["GET", "PATCH", "DELETE"],
            name=f"{name}_item" if name is not None else None,
            include_in_schema=include_in_schema)


class StaticEndpoint(Endpoint):
    """Single path."""
