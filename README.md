## FEM-project-Finite-element-method-
An attempt to code a truss physics engine similar to that of poly bridge or SAP2000. I recently got interested in these things thanks to my grandparent's inspiring civil engineering career in war time(steeped into irrigation engineering). Imagine inspecting dams when bombardiers are still flying above their land. Crazy.

# FEATURES 
- Global stiffness matrix assembly
- Matrix reduction
- Linear system solving using NumPy
- Axial force, reaction, displacement for each node
- Structural collapse (loop in the future)

# Assumptions & limitations : 
- Bars can have different cross sectional area & Young's modulous but they have to be all uniform
- Assume we do not permit rotation about each node
- No deformation, the bar breaks or remains

# From Hooke's law to linear algebra model
   At the very beginning, everything comes from a simple physical idea: if you pull on a bar, it stretches. If you push on it, it compresses. Remember the good old Hooke's law? 
Hooke’s law says that force is proportional to deformation. For a 1D bar:

F = k * ΔL

where ΔL is the change in length, and k is the stiffness of the bar. For a uniform bar, stiffness is:

k = EA / L

So we can write:

F = (EA / L) * ΔL


## Step 1: What is ΔL in a truss?

In a truss, elements are not aligned with the x or y axis. Each element is oriented in 2D space. So, how do we compute the change in length ΔL from node displacements?

Let node i have displacement (u_i, v_i) and node j have displacement (u_j, v_j).

The original element has a direction vector:

d = (x_j - x_i, y_j - y_i)

Let its length be L, and define direction cosines:

c = (x_j - x_i) / L  
s = (y_j - y_i) / L  

Now, instead of thinking in x and y separately, we use the dot product to project the displacement onto the bar's axis.

The extension ΔL is: ΔL = (u_j - u_i)*c + (v_j - v_i)*s

Still simple.... Right?
This step is extremely important: it converts 2D motion into a 1D stretch along the element.

## Step 2: From extension to force

Now plug ΔL into Hooke’s law:

F = (EA / L) * [(u_j - u_i)*c + (v_j - v_i)*s]

This F is the internal axial force in the element.

## Step 3: Distribute forces to nodes

The element pulls equally and oppositely on its two nodes.

At node i, the force is in the negative direction of the element.
At node j, the force is in the positive direction.

We project F back into x and y:

At node i:
F_ix = -F * c  
F_iy = -F * s  

At node j:
F_jx =  F * c  
F_jy =  F * s  

Now substitute F:

F_ix = -(EA / L) * [ (u_j - u_i)*c + (v_j - v_i)*s ] * c  
F_iy = -(EA / L) * [ (u_j - u_i)*c + (v_j - v_i)*s ] * s  
F_jx =  (EA / L) * [ (u_j - u_i)*c + (v_j - v_i)*s ] * c  
F_jy =  (EA / L) * [ (u_j - u_i)*c + (v_j - v_i)*s ] * s  


## Step 4: Rewriting in matrix form
Now comes the key transition to a different expression which allows us to utilize computational power.

Start from the expression of the axial force:

F = (EA / L) * [ (u_j - u_i)*c + (v_j - v_i)*s ]

Now look at the force components at node i:

F_ix = -F * c  
F_iy = -F * s  

Substitute F into F_ix:

F_ix = -(EA / L) * [ (u_j - u_i)*c + (v_j - v_i)*s ] * c  

Now distribute c into the bracket:

F_ix = -(EA / L) * [ (u_j - u_i)*c^2 + (v_j - v_i)*c*s ]

Now expand the differences:

F_ix = -(EA / L) * [ u_j*c^2 - u_i*c^2 + v_j*c*s - v_i*c*s ]

Rearrange by grouping terms x,y for each node (u_i, v_i, u_j, v_j):

F_ix = (EA / L) * [ u_i*c^2 + v_i*c*s - u_j*c^2 - v_j*c*s ]

Do the same for F_iy, we get : 

F_iy = (EA / L) * [ u_i*c*s + v_i*s^2 - u_j*c*s - v_j*s^2 ]

Do the same for node j.

OBSERVE THAT : 

Each force component is a linear combination of the four displacement variables:

u_i, v_i, u_j, v_j

For example:

F_ix = (EA / L) * [(c^2)*u_i + (c*s)*v_i + (-c^2)*u_j + (-c*s)*v_j]

F_iy = (EA / L) * [(c*s)*u_i + (s^2)*v_i + (-c*s)*u_j + (-s^2)*v_j]


Looking at each individual equations, can you recognize the matrix-vector multiplication?


On the left, group the forces:

[F_ix, F_iy, F_jx, F_jy], denote it as F_e

On the right, group the displacements:

[u_i, v_i, u_j, v_j], denote it as u_e

See it? We rewrite the entire system compactly:

F_e = k_e * u_e

Where k_e is:

k_e = (EA / L) *
[
 [ c^2,  c*s, -c^2, -c*s ],
 [ c*s,  s^2, -c*s, -s^2 ],
 [ -c^2, -c*s,  c^2,  c*s ],
 [ -c*s, -s^2,  c*s,  s^2 ]
]

This step is insightful, allowing computational power to come in play. "Magic!!!"

So the scary matrix form is rather a more sophisticated way to encode such a mess of variables and equations.

## Step 5: Generalized case

Each element only connects two nodes, but a structure has many elements.

We define a global displacement vector u:

u = [u_1, v_1, u_2, v_2, ..., u_n, v_n]

Each element contributes its k_e into a global stiffness matrix K.

This process is called assembly:
- map local DOFs → global DOFs
- add k_e into the correct positions in K

After assembling all elements, we get:

K u = F

This is the entire linear system.


## Step 6: Stress, strain, axial force, and the others...

What can we compute after solving for nodal displacement?

 1. Element extension

For each element:

ΔL = (u_j - u_i)*c + (v_j - v_i)*s

This tells us how much the element stretches or compresses.


2. Axial force

Using Hooke’s law:

F = (EA / L) * ΔL

This gives the internal force in each bar.

Positive means tension, negative means compression.


3. Stress

We can compute stress:

σ = F / A

This tells us how “intense” the force is inside the material. This determines if the bar will collapse, not merely axial force.


4. Reaction forces

Even though we remove constrained DOFs when solving, we can recover reaction forces at supports.

Plug the full displacement vector back into:

F = K u

The entries corresponding to fixed DOFs give reaction forces.


## Key notes
- Dictionary look ups are faster than indexing
- np.ix creates a matrix that is a combination of the elements input in the two input parameters
- I chose the data representation in order from the node of lowest index -> higher index. This has to be consistent throughout the project. Note that I used min, max so that whether you give me two unordered nodes, it automatically fixes.
- numpy library has some great commands when it comes to operating w/ list vectors and matrices. Reduce and global u,K for more details

