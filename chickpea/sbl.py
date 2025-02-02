import legume
from legume import backend as bd
import numpy as np

class ShapeBuilder():
    def __init__(self, **defaults):


        self._defaults = dict()

        self._defaults.update(defaults)

        raise NotImplementedError("Must be implemented by subclass")

    def place_shape(self, phc, eps, x, y, **params):
        """
        Takes in a PhotCryst object and places shapes in it.
        :param phc: PhotCryst crystal object to place shapes in.
        :param params: parameters governing shape
        :return:
        """
        raise NotImplementedError("Must be implemented by subclass")

    @property
    def bounds(self):
        """
        Get bounds on parameters
        :return: returns dictionary of bounds on parameters.
        """
        return self._bounds
    @bounds.setter
    def bounds(self, bounds):
        """
        Set bounds on parameters
        :return: returns dictionary of bounds on parameters.
        """
        self._bounds = bounds

    @property
    def defaults(self):
        """
        Returns default parameters
        :return: returns dictionary of default parameters.
        """
        return self._defaults

    @defaults.setter
    def defaults(self, **defaults):
        """
        Sets default parameters
        """
        for key in defaults.keys():
            if not self._bounds[key][0] < default[key] < self._bounds[key][1]:
                raise ValueError("Default parameter %s out of bounds" % key)

        self._defaults = defaults

    @property
    def parameters(self):
        """
        Returns keys of parameters of shapes.
        :return:
        """
        return self._parameters

    @property
    def parameter_dims(self):
        """
        Returns dimensions of parameter shapes.
        :return:
        """
        return self._parameters_dims


class hex_d6_poly(ShapeBuilder):

    def __init__(self, N_vertices, a, **defaults):
        """
        Initialize Shape Builder
        :param N_vertices:
        :param a:
        """
        self._parameters = ['lengths', 'angles']

        self._bounds = {'lengths': [(0,0.5*a)]*N_vertices,
                  'angles':  [(0,np.radians(30))]*N_vertices}


        self._parameters_dims = [N_vertices, N_vertices]


        self.N_vertices = N_vertices

        self.a = a
        self._defaults = dict()

        self._defaults.update(defaults)

    def place_shape(self, phc, eps, x, y, **params):
        """
        Takes in a PhotCryst object and places shapes in it.
        :param phc: PhotCryst crystal object to place shapes in.
        :param params: parameters governing shape
        """
        _params = dict(self.defaults)
        _params.update(params)
        lengths = _params['lengths']
        angles = _params['angles']

        vectors=[]
        for ver_ind in range(self.N_vertices):
            l, theta = lengths[ver_ind], angles[ver_ind]

            vectors.append(bd.array((l, l*bd.tan(theta))))

        rot_mat = Rmat(np.radians(60))
        flip_mat = bd.array(((1,0),(0,-1)))

        vec_mat_ = bd.vstack(vectors).T
        vec_mat = bd.hstack((vec_mat_,bd.matmul(flip_mat, vec_mat_)[:,::-1]))

        for rot_power in range(6):
            rotation = bd.linalg.matrix_power(rot_mat, rot_power)

            rot_vectors = bd.matmul(rotation, vec_mat)

            poly = legume.Poly(eps=eps, x_edges=rot_vectors[0] + x, y_edges=rot_vectors[1] + y)
            phc.add_shape(poly)


class hex_d3_poly(ShapeBuilder):

    def __init__(self, N_vertices, a, **defaults):
        """
        Initialize Shape Builder
        :param N_vertices:
        :param a:
        """
        self._parameters = ['lengths', 'angles']
        self._parameters_dims = [N_vertices, N_vertices]

        self._bounds = {'lengths': [(0,0.5*a)]*N_vertices,
                  'angles':  [(0,np.radians(60))]*N_vertices}

        self.N_vertices = N_vertices

        self.a = a
        self._defaults = dict()

        self._defaults.update(defaults)



    def place_shape(self, phc, eps, x, y, **params):
        """
        Takes in a PhotCryst object and places shapes in it.
        :param phc: PhotCryst crystal object to place shapes in.
        :param params: parameters governing shape
        """
        _params = dict(self.defaults)
        _params.update(params)

        lengths = _params['lengths']
        angles = _params['angles']

        vectors=[]
        for ver_ind in range(self.N_vertices):
            l, theta=lengths[ver_ind], angles[ver_ind]

            vectors.append(bd.array((l, l*bd.tan(theta-np.radians(30)))).T)

        rot_mat = Rmat(np.radians(120))
        flip_mat = bd.matmul(bd.matmul(Rmat(np.radians(-30)), bd.array(((1,0),(0,-1)))), Rmat(np.radians(30)))

        vec_mat_ = bd.vstack(vectors).T
        vec_mat = bd.hstack((vec_mat_,bd.matmul(flip_mat, vec_mat_)[:,::-1]))

        for rot_power in range(3):
            rotation = bd.linalg.matrix_power(rot_mat, rot_power)

            rot_vectors = bd.matmul(rotation, vec_mat)

            poly = legume.Poly(eps=eps, x_edges=rot_vectors[0] + x, y_edges=rot_vectors[1] + y)
            phc.add_shape(poly)


class hex_dual_d3_poly(ShapeBuilder):

    def __init__(self, N_vertices_1, N_vertices_2, a, **defaults):
        """
        Initialize Shape Builder
        :param N_vertices:
        :param a:
        """
        self._parameters = ['lengths_1', 'angles_1', 'lengths_2', 'angles_2']
        self._parameters_dims = [N_vertices_1, N_vertices_1, N_vertices_2, N_vertices_2]

        self._bounds = {'lengths_1': [(0,0.5*a)]*N_vertices_1,
                  'angles_1':  [(0,np.radians(30))]*N_vertices_1,
                  'lengths_2': [(0, 0.5*a)] * N_vertices_2,
                  'angles_2': [(0, np.radians(30))] * N_vertices_2,
                  }


        self.N_vertices_1 = N_vertices_1
        self.N_vertices_2 = N_vertices_2

        self.a = a
        self._defaults = dict()

        self._defaults.update(defaults)

    def place_shape(self, phc, eps, x, y, **params):
        """
        Takes in a PhotCryst object and places shapes in it.
        :param phc: PhotCryst crystal object to place shapes in.
        :param params: parameters governing shape
        """
        _params = dict(self.defaults)
        _params.update(params)

        lengths_1 = _params['lengths_1']
        lengths_2 = _params['lengths_2']

        angles_1 = _params['angles_1']
        angles_2 = _params['angles_2']

        vectors_1 = []
        for ver_ind in range(self.N_vertices_1):
            l, theta = lengths_1[ver_ind], angles_1[ver_ind]

            vectors_1.append(bd.array((l, l*bd.tan(theta))).T)


        vectors_2 = []
        for ver_ind in range(self.N_vertices_1):
            l, theta = lengths_2[ver_ind], angles_2[ver_ind]

            vectors_2.append(bd.array((l, l*bd.tan(theta))).T)

        rot_mat = Rmat(np.radians(60))

        flip_mat = bd.array(((1,0),(0,-1)))

        vec_mat_1_ = bd.vstack(vectors_1).T
        vec_mat_1 = bd.hstack((vec_mat_1_,bd.matmul(flip_mat, vec_mat_1_)[:,::-1]))

        vec_mat_2_ = bd.vstack(vectors_2).T
        vec_mat_2 = bd.hstack((vec_mat_2_,bd.matmul(flip_mat, vec_mat_2_)[:,::-1]))

        for rot_power in range(6):
            rotation = bd.linalg.matrix_power(rot_mat, rot_power)



            if rot_power % 2 == 0:
                rot_vectors = bd.matmul(rotation, vec_mat_1)
                poly = legume.Poly(eps=eps, x_edges=rot_vectors[0] + x, y_edges=rot_vectors[1] + y)
                phc.add_shape(poly)
            else:
                rot_vectors = bd.matmul(rotation, vec_mat_2)
                poly = legume.Poly(eps=eps, x_edges=rot_vectors[0] + x, y_edges=rot_vectors[1] + y)
                phc.add_shape(poly)


class diamond_d1_dual_poly(ShapeBuilder):
    def __init__(self, N_vertices_1, N_vertices_2, a, **defaults):
        """

        Initialize Shape Builder
        :param N_vertices_1:
        :param N_vertices_2:
        :param a:
        """
        self._parameters = ['lengths_1', 'angles_1', 'lengths_2', 'angles_2']
        self._parameters_dims = {'lengths_1': N_vertices_1,
                  'angles_1': N_vertices_1,
                  'lengths_2': N_vertices_2,
                  'angles_2': N_vertices_2,
                  }

        self._bounds = {'lengths_1': [(0, a)] * N_vertices_1,
                  'angles_1': [(0, np.radians(30))] * N_vertices_1,
                  'lengths_2': [(0, a)] * N_vertices_2,
                  'angles_2': [(0, np.radians(30))] * N_vertices_2,
                  }

        self.N_vertices_1 = N_vertices_1
        self.N_vertices_2 = N_vertices_2

        self.a = a
        self._defaults = dict()

        self._defaults.update(defaults)

    def place_shape(self, phc, eps, x, y, **params):
        """
        Takes in a PhotCryst object and places shapes in it.
        :param phc: PhotCryst crystal object to place shapes in.
        :param params: parameters governing shape
        """
        _params = dict(self.defaults)
        _params.update(params)
        lengths_1 = _params['lengths_1']
        lengths_2 = _params['lengths_2']

        angles_1 = _params['angles_1']
        angles_2 = _params['angles_2']

        vectors_1 = []
        for ver_ind in range(self.N_vertices_1):
            l, theta = lengths_1[ver_ind], angles_1[ver_ind]

            vectors_1.append(bd.array((l, l * bd.tan(theta))).T)

        vectors_2 = []
        for ver_ind in range(self.N_vertices_1):
            l, theta = lengths_2[ver_ind], angles_2[ver_ind]

            vectors_2.append(bd.array((l, l * bd.tan(theta))).T)

        flip_mat_1 = bd.matmul(bd.matmul(Rmat(np.radians(30)), bd.array(((1, 0), (0, -1)))), Rmat(np.radians(-30)))

        flip_mat_2 = bd.matmul(bd.matmul(Rmat(np.radians(120)), bd.array(((1, 0), (0, -1)))), Rmat(np.radians(-120)))

        shift_stack = bd.vstack(list(bd.array([self.a, 0]) for i in range(2*self.N_vertices_1))).T

        # Construct vertices of first polygon

        vec_mat_1_ = bd.vstack(vectors_1).T
        vec_mat_1_ = bd.matmul(Rmat(np.radians(30)), vec_mat_1_)
        # Apply mirror symmetry
        vec_mat_1 = bd.hstack((vec_mat_1_, bd.matmul(flip_mat_1, vec_mat_1_)[:, ::-1])) - shift_stack

        # Construct vertices of second polygon
        vec_mat_2_ = bd.vstack(vectors_2).T
        vec_mat_2_ = bd.matmul(Rmat(np.radians(30)), vec_mat_2_)
        # Apply mirror symmetry
        vec_mat_2_ = bd.hstack((vec_mat_2_, bd.matmul(flip_mat_1, vec_mat_2_)[:, ::-1])) - shift_stack

        # Send vertices to appropriate region of the diamond.
        vec_mat_2 = (bd.matmul(flip_mat_2, vec_mat_2_))[:,::-1]

        poly = legume.Poly(eps=eps, x_edges=vec_mat_2[0] + x, y_edges=vec_mat_2[1] + y)
        phc.add_shape(poly)

        poly = legume.Poly(eps=eps, x_edges=vec_mat_1[0] + x, y_edges=vec_mat_1[1] + y)
        phc.add_shape(poly)


class dual_circle(ShapeBuilder):
    def __init__(self, a, **defaults):
        """
        Initialize Shape Builder
        :param a: lattice constant
        """
        self._parameters = ['length_1', 'angle_1', 'radius_1', 'length_2', 'angle_2', 'radius_2']
        self._parameters_dims = {'length_1': 1,
                  'angle_1': 1,
                  'radius_1': 1,
                  'length_2': 1,
                  'angle_2': 1,
                  'radius_2': 1
                  }
        self._bounds = {'length_1': [(0, a*np.sqrt(3)/2)] ,
                  'angle_1': [(0, np.radians(60))],
                  'radius_1': [(0, a*np.sqrt(3)/6)],
                  'length_2': [(0, a*np.sqrt(3)/4)],
                  'angle_2': [(0, np.radians(60))],
                  'radius_2': [(0, a*np.sqrt(3)/6)]
                  }


        self.a = a
        self._defaults = {'length_1': a/np.sqrt(3),
                  'angle_1': np.radians(30),
                  'radius_1': a*np.sqrt(3)/6,
                  'length_2': a/np.sqrt(3),
                  'angle_2': np.radians(30),
                  'radius_2': a*np.sqrt(3)/6
                  }

        self._defaults.update(defaults)

    def place_shape(self, phc, eps, x, y, **params):
        """
        Takes in a PhotCryst object and places shapes in it.
        :param phc: PhotCryst crystal object to place shapes in.
        :param params: parameters governing shape
        """
        _params = dict(self.defaults)
        _params.update(params)

        length_1 = _params['length_1']
        length_2 = _params['length_2']
        angle_1 = _params['angle_1']
        angle_2 = _params['angle_2']
        radius_1 = _params['radius_1']
        radius_2 = _params['radius_2']

        vector_1 = bd.array((length_1, length_1 * bd.tan(angle_1 - np.radians(30)))).flatten()
        vector_2 = bd.array((length_2, length_2 * bd.tan(angle_2 - np.radians(30)))).flatten()
        vector_2 = bd.array((self.a*np.sqrt(3),0)) - vector_2
        vector_1 = bd.matmul(Rmat(np.radians(30)), vector_1)
        vector_2 = bd.matmul(Rmat(np.radians(30)), vector_2)

        Circle = legume.Circle(eps=eps, x_cent=vector_1[0] + x, y_cent=vector_1[1] + y, r=radius_1)
        phc.add_shape(Circle)

        Circle = legume.Circle(eps=eps, x_cent=vector_2[0] + x, y_cent=vector_2[1] + y, r=radius_2)
        phc.add_shape(Circle)



def Rmat(rot_ang, deg_rad='rad'):
    c, s = bd.cos(rot_ang), bd.sin(rot_ang)
    return bd.array(((c, -s), (s, c)))