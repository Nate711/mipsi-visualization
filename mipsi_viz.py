# IMPORT PACKAGES
import numpy as np
import pandas as pd

import meshcat
import meshcat.geometry as g
import meshcat.transformations as tf
from meshcat import animation

if __name__ == "__main__":

    # IMPORT MG OUTPUT
    cols = "t sec, qA deg, qB deg, qA' deg/sec, qB' deg/sec, vx m/s, TC N*m, TD N*m, x m, y m"

    df = pd.read_csv('ODE.1', delim_whitespace=True, header=None, skiprows=4)
    cols = [c.strip() for c in cols.split(",")]
    df.columns = cols

    # PLOT Ao PATH POINT
    pd.options.plotting.backend = "plotly"
    fig = df.plot.line(x='x m', y='y m', title='Bo Path Point')
    fig.show()

    # PLOT BODY PITCH
    fig2 = df.plot.line(x='t sec', y='qB deg', title='B Pitch')
    fig2.show()

    # CREATE NEW VISUALIZER
    vis = meshcat.Visualizer()

    # DECLARE CONSTANTS
    LZ = 0.2
    LX = 0.1
    LY = 0.1
    WHEEL_RAD = 0.05
    WHEEL_THICKNESS = 0.01
    D = 0.16
    FRAME_RATE = 30

    # CREATE OBJECTS IN ENVIRONMENT
    # Robot Body
    vis["B"].set_object(g.Box([LX, LY, LZ]))
    # Robot Left Wheel
    vis["C"].set_object(g.Cylinder(WHEEL_THICKNESS, WHEEL_RAD))
    # Robot Right Wheel
    vis["D"].set_object(g.Cylinder(WHEEL_THICKNESS, WHEEL_RAD))

    # ANIMATE SIMULATION
    anim = animation.Animation(clips=None, default_framerate=FRAME_RATE)

    for i in range(1, df.shape[0]):
        r_No_Ao = np.array((df["x m"][i], df["y m"][i], WHEEL_RAD))
        qA = df["qA deg"][i] * np.pi/180
        qB = df["qB deg"][i] * np.pi/180
        A_N = np.array([[np.cos(qA), np.sin(qA), 0],
                        [-np.sin(qA), np.cos(qA), 0],
                        [0, 0, 1.0]])
        B_A = np.array([[np.cos(qB), 0, -np.sin(qB)],
                        [0, 1.0, 0],
                        [np.sin(qB), 0, np.cos(qB)]])
        N_A = A_N.T
        A_B = B_A.T
        N_B = np.matmul(N_A, A_B)
        eulerAngles = tf.euler_from_matrix(N_B, axes='sxyz')
        r_No_Bcm = r_No_Ao + LZ / 2 * N_B[:, 2].T
        r_No_Ccm = r_No_Ao + D / 2 * A_N[1, :].T
        r_No_Dcm = r_No_Ao - D / 2 * A_N[1, :].T

        with anim.at_frame(vis, i) as frame:
            transMatB = tf.compose_matrix(scale=None,
                                          shear=None,
                                          angles=eulerAngles,
                                          translate=r_No_Bcm,
                                          perspective=None)
            frame["B"].set_transform(transMatB)

            transMatC = tf.compose_matrix(scale=None,
                                          shear=None,
                                          angles=eulerAngles,
                                          translate=r_No_Ccm,
                                          perspective=None)
            frame["C"].set_transform(transMatC)

            transMatD = tf.compose_matrix(scale=None,
                                          shear=None,
                                          angles=eulerAngles,
                                          translate=r_No_Dcm,
                                          perspective=None)
            frame["D"].set_transform(transMatD)

        vis.set_animation(anim)
    print("Click 'Open Controls' in the top-right of the window to view the animation controls")
    input("Press enter to kill the simulation")