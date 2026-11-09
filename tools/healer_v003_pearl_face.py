"""Fit a browless pearl mannequin face beneath the existing brow-length hood."""
import math
import bpy

group = bpy.data.collections['V003 - fitting 04 tailored']
name = 'Healer - pearl face'
assert name not in group.objects
mat = bpy.data.materials.new('Healer - satin pearl')
mat.use_nodes = True
shader = next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
mat.diffuse_color = (.84,.83,.80,1)
shader.inputs['Base Color'].default_value = mat.diffuse_color
shader.inputs['Roughness'].default_value = .44
shader.inputs['Coat Weight'].default_value = .14
shader.inputs['Coat Roughness'].default_value = .34

# Closed cross sections run up from the neck, beneath the chin, and over the skull.
# Each gives width, foremost surface, and rear surface in scene coordinates.
profiles = [(1.690,.052,-.058,.045),(1.750,.045,-.061,.041),
 (1.793,.042,-.065,.039),(1.813,.040,-.076,.038),(1.823,.028,-.104,.040),
 (1.833,.035,-.115,.044),(1.851,.049,-.121,.052),(1.875,.057,-.122,.060),
 (1.900,.067,-.124,.066),(1.935,.079,-.125,.071),(1.967,.082,-.124,.074),
 (2.007,.080,-.127,.071),(2.037,.068,-.119,.061),(2.065,.044,-.091,.042),
 (2.080,.006,-.042,-.022)]
def profile(z):
    for i,(a,b) in enumerate(zip(profiles,profiles[1:])):
        if z<=b[0]:
            t=(z-a[0])/(b[0]-a[0])
            prev=profiles[max(0,i-1)]
            nxt=profiles[min(len(profiles)-1,i+2)]
            dz=b[0]-a[0]
            return [((2*t-3)*t*t+1)*a[k]+(3-2*t)*t*t*b[k]
                    +(t-1)**2*t*dz*(b[k]-prev[k])/(b[0]-prev[0])
                    +(t-1)*t*t*dz*(nxt[k]-a[k])/(nxt[0]-a[0]) for k in (1,2,3)]
    return profiles[-1][1:]
def g(x,w):
    return math.exp(-(x/w)**2)
def relief(x,z):
    # Sweep the cheek highlight up toward the temple, with hollow beneath it.
    side=abs(x)
    cheek_z=1.923+.20*(side-.040)
    cheek=.011*g(side-.036,.032)*g(z-cheek_z+.006,.030)
    hollow=-.0008*g(side-.047,.022)*g(z-1.889,.026)
    orbit=-.0028*g(side-.034,.022)*g(z-1.953,.014)
    bridge=.013*g(x,.0105)*g(z-1.941,.035)
    tip=.0175*g(x,.0125)*g(z-1.916,.013)
    wing=.0048*g(side-.010,.0065)*g(z-1.908,.0065)
    chin=.0038*g(x,.020)*g(z-1.840,.012)-.0015*g(x,.018)*g(z-1.856,.007)
    return cheek+hollow+orbit+bridge+tip+wing+chin
vs=[];fs=[]
rows,cols=250,224
for j in range(rows):
    z=1.690+.390*j/(rows-1)
    width,front,back=profile(z)
    for i in range(cols):
        a=math.tau*i/cols
        c=math.cos(a)
        x=width*math.sin(a)
        y=(back+front)/2-(back-front)/2*c
        if c>0:
            y-=c**2*relief(x,z)
        # Bring the chin gently toward the mouth to shorten the lower face.
        chin_lift=.009*g(z-1.832,.029)*max(0,c)
        vs.append((x,y,z+chin_lift))
        if j:
            k=j*cols+i
            h=j*cols+(i+1)%cols
            fs.append((k-cols,h-cols,h,k))
fs.extend([tuple(reversed(range(cols))),tuple(range((rows-1)*cols,rows*cols))])
mesh=bpy.data.meshes.new('Continuous pearl head and neck')
mesh.from_pydata(vs,[],fs)
mesh.update()
obj=bpy.data.objects.new(name,mesh)
group.objects.link(obj)
mesh.materials.append(mat)
for p in mesh.polygons:
    p.use_smooth=True
veil=group.objects['Fit04 opaque shaped face veil - no facial features']
veil.hide_render=True
veil.hide_set(True)
veil.hide_viewport=True
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
