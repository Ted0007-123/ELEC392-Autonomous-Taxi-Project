# Autonomous Taxi Software Project

This repository contains the source code for a team-based ELEC 392 Autonomous Taxi project at Queen’s University.

The project used a small-scale autonomous vehicle platform and focused on navigation, fare/task selection, safety behavior, sensor-based decision-making, and system integration.

This repository only includes the source code. Large training files, images, datasets, and hardware-specific files are not included.

## Project Overview

The autonomous taxi system was designed to support basic autonomous taxi behavior, including selecting a fare, calculating routes, sending navigation decisions to the control system, checking safety conditions, and providing vehicle status feedback.

Some parts of the project require the original Raspberry Pi-based vehicle platform and related hardware dependencies to run properly.

## My Contributions

This was a team project. My main contributions were in the following areas:

## 1. Optimization

Relevant folder:

```text
src/optimization/
```

The optimization module was my largest contribution to the project.

The purpose of this module was to decide the route the vehicle should take and provide that route to the control/navigation part of the system. It handled two main route-planning stages: from the vehicle’s current position to the customer pickup point, and from the pickup point to the customer’s destination.

To support this, I converted the course-provided map into a coordinate-based one-way graph representation. Using this graph, the module applied Dijkstra’s algorithm to find efficient routes through the road network. This allowed the system to calculate travel paths based on the map structure rather than relying on hard-coded movement instructions.

The optimization module also supported fare selection. Since the taxi needed to choose between possible fares, the module considered both cost and return when helping the higher-level logic decide which fare was most worthwhile to accept. In this way, the module connected route planning with task selection and helped the overall system make more practical navigation decisions.

In short, this module acted as the decision-making layer between the map/fare information and the vehicle control logic.

## 2. Safety Module

Relevant folder:

```text
src/safety_module/
```

I worked on safety-related software that helped determine whether the vehicle should continue moving, slow down, or stop.

This included emergency stop behavior, ultrasonic obstacle detection, vision-related safety states, and navigation permission logic.

## 3. LED Control

Relevant folder:

```text
src/LED_Control/
```

I worked on the LED control module used for vehicle status feedback.

This included brake lights, signal lights, hazard lights, headlights, and general lighting behavior used to make the vehicle’s current state easier to observe during testing and operation.

## Technologies Used

* Python
* Graph-based route planning
* Dijkstra’s algorithm
* Raspberry Pi-based vehicle platform
* PiCar-X / Robot Hat hardware
* Ultrasonic sensor
* Camera-based detection
* Basic multithreading and system integration

## Notes

This project was built for a specific hardware setup, so it is not intended to run as a complete standalone application on a normal laptop.

The purpose of this repository is to show the source code structure and my main software contributions in a team-based autonomous vehicle project.
