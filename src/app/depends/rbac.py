# import third-party libraries
from fastapi import (
    Request, 
    WebSocket,
)
from fastapi.exceptions import HTTPException
from fastapi.responses import (
    RedirectResponse,
    HTMLResponse,
)

# import local Python libraries
import utils.constants as C
from utils.jinja2_helper import (
    url_for,
    render_template,
)

# import Python's standard libraries
from typing import Any # TODO: to remove

async def verify_access(
    request: Request | WebSocket,
    role_arr: set[str] | str,
    col: Any | None = None,
    clear_session_if_invalid: bool | None = True,
    admin_db: Any | None = None,
) -> None | RedirectResponse:
    """Verifies the user's access based on their role.

    Args:
        request (Request | WebSocket):
            The user's request to retrieve the session ID from and
            to authorise the user based on their given roles.
        role_arr (tuple[str] | str):
            The list of roles that are allowed to access the route.
            If a string is passed, it will be converted to a list.
        clear_session_if_invalid (bool, optional):
            Whether to clear the session if the session ID is invalid.
            Defaults to True.
        admin_db (Database, optional):
            The admin database to use to get the user document.
            Defaults to None. If None, a new admin database client will be created.

    Returns:
        None | RedirectResponse:
            Returns X from database if the user is logged in or
            redirects the user to the home page if they are not authorised.

    Raises:
        UserBannedException:
            If the user is banned.
    """
    if isinstance(role_arr, str):
        role_arr = (role_arr,)
    else:
        role_arr = role_arr

    session_id = request.session.get(C.SESSION_COOKIE, None)
    # TODO: Get user info from session id
    user_info = request.session.get(session_id)

    
    user_roles = (C.GUEST,) # <- dummy data
    for role in user_roles:
        if role in role_arr:
            return RBACResults() # <- Might want to return an initialised user object instead
    return RedirectResponse(url="/")

class RBACResults:
    def __init__(self) -> None:
        """Initialises the RBACResults class."""
        self.__user_info = None # TODO: Add user info here
        self.__email = None
        self.__username = None
        self.__role = None

class RBACDepends:
    def __init__(self, role_arr: tuple[str] | str, default_endpoint: str | None = None, sensitive: bool | None = False) -> None:
        """Initialises the RBAC_Depends class.

        Args:
            role_arr (tuple[str] | str):
                The list of roles that are allowed to access the route.
                If a string is passed, it will be converted to a list.
            default_endpoint (str | None):
                The default endpoint/function name to redirect the user to if they are not authorised.
                Defaults to "index".
            sensitive (bool, optional):
                Whether the route is sensitive or not.
                Will raise a 404 error if the route is sensitive and the user is not authorised.
        """
        self.__role_arr = role_arr
        self.__sensitive = sensitive
        self.__default_endpoint = default_endpoint or "index"
        self.__cached_endpoint_url = {} # type: dict[str, str]

    def get_endpoint_url(self, request: Request, endpoint: str) -> str:
        """Returns the endpoint's URL with a
        slight performance gain by caching the url_for() result.

        Args:
            request (Request):
                The request object.
            endpoint (str):
                The endpoint/function name.

        Returns:
            str:
                The endpoint's URL.
        """
        if endpoint not in self.__cached_endpoint_url:
            # just for slight optimisation
            self.__cached_endpoint_url[endpoint] = url_for(
                request=request,
                name=endpoint,
            )
        return self.__cached_endpoint_url[endpoint]

    def return_redirect_response(self, request: Request) -> RedirectResponse:
        """Returns a RedirectResponse to the default endpoint.

        Args:
            request (Request):
                The request object.

        Returns:
            RedirectResponse:
                A RedirectResponse to the default endpoint.

        Raises:
            HTTPException:
                If the route is sensitive and the user is not authorised.
        """
        if self.__sensitive:
            raise HTTPException(
                status_code=404,
                detail="Not found",
            )
        return RedirectResponse(
            url=self.get_endpoint_url(request, self.__default_endpoint),
        )

    async def __call__(self, request: Request) -> None | RedirectResponse | RBACResults:
        """Verifies if the user is authorised to access the route.

        Args:
            request (Request):
                The request object.

        Returns:
            None | RedirectResponse | RBACResults:
                RBACResults if the user is authorised to access the route.
                RedirectResponse (if the default_endpoint was given) if the user is not authorised to access the route.
        """
        if C.SESSION_COOKIE not in request.session:
            # not logged in
            if C.GUEST in self.__role_arr:
                return RBACResults()

            # Not authorised to view the route
            return self.return_redirect_response(
                request=request,
            )

        # TODO: Get user role from database and check with self.__role_arr
        return

        # Not authorised to view the route
        return self.return_redirect_response(
            request=request,
        )

RBAC_TYPING = None | RedirectResponse | RBACResults
ALLROLES_RBAC = RBACDepends(
    role_arr=C.ALLROLES,
    default_endpoint="index",
)
GUEST_RBAC = RBACDepends(
    role_arr=(C.GUEST,),
    default_endpoint="index",
)
USER_RBAC = RBACDepends(
    role_arr=(C.USER,),
    default_endpoint="login",
)
ADMIN_RBAC = RBACDepends(
    role_arr=(C.ADMIN,),
    sensitive=True,
    default_endpoint="login",
)
