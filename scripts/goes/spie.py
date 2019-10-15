from sympy import *



def test():
    phi = Symbol('phi')
    theta = Symbol('theta')
    r_ele = Symbol('r_ele')
    r_ple = Symbol('r_ple')
    r_egrs = Symbol('r_egrs')
    r_pgrs = Symbol('r_pgrs')
    ff_le = Symbol('ff_le')
    ff_grs = Symbol('ff_grs')
    phi_p = Symbol('phi_p')
    theta_p = Symbol('theta_p')

    ff_le = (r_ele - r_ple) / r_ele

    ff_grs = (r_egrs - r_pgrs) / r_egrs

    phi_p = atan(((1 - ff_grs)**2) * tan(phi))

    P_e = Symbol('P_e')


    P_e_it =[
                [P_e * cos(phi_p) * cos(theta_p)],
                [P_e * cos(phi_p) * sin(theta_p)],
                [P_e * sin(phi_p)]
            ]

    print(P_e_it)


def nav_fg():
    D_nom   = Symbol('D_nom')
    P       = Symbol('P')
    R_nom   = Symbol('R_nom')
    phi_p   = Symbol('phi_p')
    theta_p = Symbol('theta_p')
    lam     = Symbol('lambda')
    # lam = -1.308996939
    lam = 0

    P_it = Matrix([
                      [P * cos(phi_p) * cos(theta_p)],
                      [P * cos(phi_p) * sin(theta_p)],
                      [P * sin(phi_p)]
                  ])

    # R_nom = 42164160
    R_nom_it = Matrix([
                          [R_nom * cos(lam)],
                          [R_nom * sin(lam)],
                          [0]
                      ])


    D_nom_it = P_it - R_nom_it

    # print(D_nom_it)
    # lam = -1.47813561 - -1.308996939
    A_it_fg = Matrix([
                         [ -sin(lam),  cos(lam),         0],
                         [         0,         0,        -1],
                         [ -cos(lam), -sin(lam),         0]
                     ])



    D_nom_fg = A_it_fg * D_nom_it

    print("D_nom_fg")
    for r in D_nom_fg:
        print('     {}'.format(r))

    # print(D_nom_fg[1])
    # print(D_nom_fg[2])

    # v_it = D_nom_it / D_nom_it.magnitude()

    # v_gf = A_it_fg * D_nom_it
    #
    # print("v_gf")
    # for r in v_gf:
    #     print('     {}'.format(r))



nav_fg()
