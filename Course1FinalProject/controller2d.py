#!/usr/bin/env python3

"""
2D Controller Class to be used for the CARLA waypoint follower demo.
"""

from matplotlib.pyplot import step
import cutils
import numpy as np
import math

class Controller2D(object):
    def __init__(self, waypoints):
        self.vars                = cutils.CUtils()
        self._current_x          = 0
        self._current_y          = 0
        self._current_yaw        = 0
        self._current_speed      = 0
        self._desired_speed      = 0
        self._current_frame      = 0
        self._current_timestamp  = 0
        self._start_control_loop = False
        self._set_throttle       = 0
        self._set_brake          = 0
        self._set_steer          = 0
        self._waypoints          = waypoints
        self._conv_rad_to_steer  = 180.0 / 70.0 / np.pi
        self._pi                 = np.pi
        self._2pi                = 2.0 * np.pi

    def update_values(self, x, y, yaw, speed, timestamp, frame):
        self._current_x         = x
        self._current_y         = y
        self._current_yaw       = yaw
        self._current_speed     = speed
        self._current_timestamp = timestamp
        self._current_frame     = frame
        if self._current_frame:
            self._start_control_loop = True

    def update_desired_speed(self):
        min_idx       = 0
        min_dist      = float("inf")
        desired_speed = 0
        for i in range(len(self._waypoints)):
            dist = np.linalg.norm(np.array([
                    self._waypoints[i][0] - self._current_x,
                    self._waypoints[i][1] - self._current_y]))
            if dist < min_dist:
                min_dist = dist
                min_idx = i
        if min_idx < len(self._waypoints)-1:
            desired_speed = self._waypoints[min_idx][2]
        else:
            desired_speed = self._waypoints[-1][2]
        self._desired_speed = desired_speed

    def update_waypoints(self, new_waypoints):
        self._waypoints = new_waypoints

    def get_commands(self):
        return self._set_throttle, self._set_steer, self._set_brake

    def set_throttle(self, input_throttle):
        # Clamp the throttle command to valid bounds
        throttle           = np.fmax(np.fmin(input_throttle, 1.0), 0.0)
        self._set_throttle = throttle

    def set_steer(self, input_steer_in_rad):
        # Covnert radians to [-1, 1]
        input_steer = self._conv_rad_to_steer * input_steer_in_rad

        # Clamp the steering command to valid bounds
        steer           = np.fmax(np.fmin(input_steer, 1.0), -1.0)
        self._set_steer = steer

    def set_brake(self, input_brake):
        # Clamp the steering command to valid bounds
        brake           = np.fmax(np.fmin(input_brake, 1.0), 0.0)
        self._set_brake = brake

    def update_controls(self):
        ######################################################
        # RETRIEVE SIMULATOR FEEDBACK
        ######################################################
        x               = self._current_x
        y               = self._current_y
        yaw             = self._current_yaw
        v               = self._current_speed
        self.update_desired_speed()
        v_desired       = self._desired_speed
        t               = self._current_timestamp
        waypoints       = self._waypoints
        throttle_output = 0
        steer_output    = 0
        brake_output    = 0

        ######################################################
        ######################################################
        # MODULE 7: DECLARE USAGE VARIABLES HERE
        ######################################################
        ######################################################
        """
            Use 'self.vars.create_var(<variable name>, <default value>)'
            to create a persistent variable (not destroyed at each iteration).
            This means that the value can be stored for use in the next
            iteration of the control loop.

            Example: Creation of 'v_previous', default value to be 0
            self.vars.create_var('v_previous', 0.0)

            Example: Setting 'v_previous' to be 1.0
            self.vars.v_previous = 1.0

            Example: Accessing the value from 'v_previous' to be used
            throttle_output = 0.5 * self.vars.v_previous
        """
        self.vars.create_var('v_previous', 0.0)
        self.vars.create_var('v_diff_previous', 0.0)
        self.vars.create_var('step', 0)

        # Skip the first frame to store previous values properly
        if self._start_control_loop:
            """
                Controller iteration code block.

                Controller Feedback Variables:
                    x               : Current X position (meters)
                    y               : Current Y position (meters)
                    yaw             : Current yaw pose (radians)
                    v               : Current forward speed (meters per second)
                    t               : Current time (seconds)
                    v_desired       : Current desired speed (meters per second)
                                      (Computed as the speed to track at the
                                      closest waypoint to the vehicle.)
                    waypoints       : Current waypoints to track
                                      (Includes speed to track at each x,y
                                      location.)
                                      Format: [[x0, y0, v0],
                                               [x1, y1, v1],
                                               ...
                                               [xn, yn, vn]]
                                      Example:
                                          waypoints[2][1]: 
                                          Returns the 3rd waypoint's y position

                                          waypoints[5]:
                                          Returns [x5, y5, v5] (6th waypoint)
                
                Controller Output Variables:
                    throttle_output : Throttle output (0 to 1)
                    steer_output    : Steer output (-1.22 rad to 1.22 rad)
                    brake_output    : Brake output (0 to 1)
            """

            ######################################################
            ######################################################
            # MODULE 7: IMPLEMENTATION OF LONGITUDINAL CONTROLLER HERE
            ######################################################
            ######################################################
            """
                Implement a longitudinal controller here. Remember that you can
                access the persistent variables declared above here. For
                example, can treat self.vars.v_previous like a "global variable".
            """

            #use PI controller with feedforward. assume v range between 0 - 25 m/s
            
            pGain = 0.6
            iGain = 0.01
            dGain = 1
            feedForwardGain = 0.05
            normalizeFactor = 16.25 / 2 / 5
            throttle = pGain * (v_desired - v)  + dGain * (v - self.vars.v_previous) + iGain * self.vars.v_diff_previous
            throttlePercent = throttle / normalizeFactor #normalize it back to percentage of 0-1

            if throttlePercent > 1.0:
                throttlePercent = 1.0
            elif throttlePercent < 0.0:
                throttlePercent = 0.0
            
            # Change these outputs with the longitudinal controller. Note that
            # brake_output is optional and is not required to pass the
            # assignment, as the car will naturally slow down over time.
            throttle_output = throttlePercent
            brake_output    = 0

            ######################################################
            ######################################################
            # MODULE 7: IMPLEMENTATION OF LATERAL CONTROLLER HERE
            ######################################################
            ######################################################
            """
                Implement a lateral controller here. Remember that you can
                access the persistent variables declared above here. For
                example, can treat self.vars.v_previous like a "global variable".
            """
            
            if int(self.vars.step / 3) < (len(waypoints) - 1):
                waypoint = waypoints[int(self.vars.step / 3)]
            else: 
                waypoint = waypoints[len(waypoints) - 1]

            #pure pursuit 

            processed_yaw = -yaw - np.pi / 2
            #processed_yaw = np.pi / 2
            if np.abs(processed_yaw) < 0.05:
                processed_yaw = 0
            rearAxialX = x - np.cos(processed_yaw) * 1.5
            rearAxialY = y - np.sin(processed_yaw) * 1.5
            lookAheadX = waypoint[0]
            lookAheadY = waypoint[1]
            
            L = 3 
            kdd = 0.8
            vector_ld = [lookAheadX - rearAxialX , lookAheadY - rearAxialY]
            vector_l = [x - rearAxialX, y - rearAxialY]
            ld = np.linalg.norm(vector_ld)
            #unit_vector_ld = vector_ld / ld 
            #unit_vector_l = vector_l / np.linalg.norm(vector_l)
            #dot_product = np.dot(unit_vector_ld,unit_vector_l)
            #alpha = np.arccos(dot_product) #arccos can only be positive 

            alpha = math.atan2(lookAheadX - x, lookAheadY - y) - processed_yaw

            #if lookAheadX < rearAxialX:
            #    alpha = -alpha

            #initially if v_desired is too small, will amplify alpha and cause problem 
            velocity = v_desired
            if velocity < 10.0:
                velocity = 10.0

            steer_angle = np.arctan(2 * L * np.sin(alpha) / (kdd * velocity))
            #steer_angle = np.arctan(2 * L * np.sin(alpha) / ld)

            if self.vars.step < 100:
                steer_angle = 0
            
            if steer_angle > 0.3:
                steer_angle = 0.3
            elif steer_angle < -0.3:
                steer_angle = -0.3
            
            if np.abs(steer_angle) < 0.05:
                steer_angle = 0
            
            # Change the steer output with the lateral controller. 
            steer_output = steer_angle

            #print("alpha:", alpha, " processed yaw: ", processed_yaw, " ld: ", ld, " steering angle: ", steer_angle)
            #print("waypoint x: ", lookAheadX, " waypoint y: ", lookAheadY, " current x: ", x, " current y: ", y, " rear axial x: ", rearAxialX, " rear axial y: ", rearAxialY)

            ######################################################
            # SET CONTROLS OUTPUT
            ######################################################
            self.set_throttle(throttle_output)  # in percent (0 to 1)
            self.set_steer(steer_output)        # in rad (-1.22 to 1.22)
            self.set_brake(brake_output)        # in percent (0 to 1)

        ######################################################
        ######################################################
        # MODULE 7: STORE OLD VALUES HERE (ADD MORE IF NECESSARY)
        ######################################################
        ######################################################
        """
            Use this block to store old values (for example, we can store the
            current x, y, and yaw values here using persistent variables for use
            in the next iteration)
        """
        self.vars.v_previous = v  # Store forward speed to be used in next step
        self.vars.v_diff_previous = v_desired - v + self.vars.v_diff_previous #accumulative error for Integrator part
        self.vars.step += 1
