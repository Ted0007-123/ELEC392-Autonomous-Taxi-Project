import navigation_objects as nav


def create_line_travel(
    controller,
    car_model,
    goal,
    radius=20,
    speed=20,
    timestep=0.1
):
    """
    Factory for Navigation_Line_Travel.

    Args:
        controller  : controller object (must expose .px and .navigation_allowed)
        car_model   : car model instance
        goal        : (x, y) target coordinate tuple/list
        radius      : arrival radius in cm (default 20)
        speed       : drive speed 0-100 (default 20)
        timestep    : control loop timestep in seconds (default 0.1)

    Returns:
        Navigation_Line_Travel instance (not yet started)

    Example:
        nav_obj = create_line_travel(ctrl, car, goal=(100, 200), speed=30)
        nav_obj.start()
        nav_obj._loop()
    """
    return nav.Navigation_Line_Travel(
        controller=controller,
        carModel=car_model,
        goal=goal,
        radus=radius,
        speed=speed,
        Timestep=timestep
    )


def create_atob_travel(
    controller,
    car_model,
    point=(40, 40),
    timestep=0.1
):
    """
    Factory for Navigation_AtoB_simple_Travel.

    Args:
        controller  : controller object (must expose .px and .navigation_allowed)
        car_model   : car model instance
        point       : (x, y) target coordinate tuple/list (default (40, 40))
        timestep    : control loop timestep in seconds (default 0.1)

    Returns:
        Navigation_AtoB_simple_Travel instance (not yet started)

    Example:
        nav_obj = create_atob_travel(ctrl, car, point=(150, 75), timestep=0.05)
        nav_obj.start()
        nav_obj._loop()
    """
    return nav.Navigation_AtoB_simple_Travel(
        controller=controller,
        carModel=car_model,
        point=list(point),
        Timestep=timestep
    )


# ---------------------------------------------------------------------------
# Quick-launch wrappers — create AND start in one call
# ---------------------------------------------------------------------------

def run_line_travel(controller, car_model, goal, radius=20, speed=20, timestep=0.1):
    """Creates and starts a Navigation_Line_Travel instance."""
    nav_obj = create_line_travel(controller, car_model, goal, radius, speed, timestep)
    nav_obj.start()
    nav_obj._loop()          # blocks until nav_obj.stop() is called internally
    return nav_obj.car       # returns updated car model when done


def run_atob_travel(controller, car_model, point=(40, 40), timestep=0.1):
    """Creates and starts a Navigation_AtoB_simple_Travel instance."""
    nav_obj = create_atob_travel(controller, car_model, point, timestep)
    nav_obj.start()
    nav_obj._loop()          # blocks until nav_obj.stop() is called internally
    return nav_obj.car       # returns updated car model when done



run_atob_travel()
