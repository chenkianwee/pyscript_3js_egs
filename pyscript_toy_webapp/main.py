import random
import asyncio
import numpy as np 

from pyodide.ffi.wrappers import add_event_listener

from pyscript import window, document, PyWorker
from pyscript.ffi import create_proxy

from pyscript.js_modules import three as THREE
from pyscript.js_modules.oc import OrbitControls

# get the renderer and append it to index.html
renderer = THREE.WebGLRenderer.new(antialias=True)
renderer.setSize(window.innerWidth, window.innerHeight*0.85)
bottom_side = document.getElementById('bottomSide')
bottom_side.appendChild(renderer.domElement)
# get the camera and scene
camera = THREE.PerspectiveCamera.new(35, window.innerWidth / window.innerHeight, 0.1, 1000)
camera.position.set(1, 1, 5)
# get the scene
scene = THREE.Scene.new()
# get lights and put in the scene
light_back_green = THREE.PointLight.new(0x00FF00, 1, 1000)
light_back_green.decay = 3.0
light_back_green.position.set(5, 0, 2)
light_back_white = THREE.PointLight.new(0xFFFFFF, 5, 1000)
light_back_white.decay = 20.0
light_back_white.position.set(5, 0, 2)
scene.add(light_back_green)
scene.add(light_back_white)
# Orbit Controls
controls = OrbitControls.new(camera, renderer.domElement)
controls.enableDamping = True
controls.dampingFactor = 0.04
# generate points
poss = []
for _ in range(1500):
    poss.append(random.random() * 6) 
    poss.append(random.random() * 6) 
    poss.append(random.random() * 6)

geometry = THREE.BufferGeometry.new()
poss = window.Float32Array.new(poss)
geometry.setAttribute('position', THREE.BufferAttribute.new(poss, 3))
material = THREE.PointsMaterial.new(color = THREE.Color.new(1,0,0), size = 0.1, sizeAttenuation = True)
threejs_pts = THREE.Points.new(geometry, material)
scene.add(threejs_pts)
# generate a cube
geometry = THREE.BoxGeometry.new(1, 1, 1)
material = THREE.MeshBasicMaterial.new(color = THREE.Color.new(0.5,0.5,0.5))
cube = THREE.Mesh.new(geometry, material)
scene.add(cube)
# generate the edges of a cube
edges = THREE.EdgesGeometry.new(geometry)
line_material = THREE.LineBasicMaterial.new(color = THREE.Color.new(1,1,0))
cube_edges = THREE.LineSegments.new(edges, line_material)
scene.add(cube_edges)

camera.lookAt(scene.position)

async def get_bytes_from_file(item) -> bytes:
    array_buf = await item.arrayBuffer()
    return array_buf.to_bytes()

async def on_pts_submit(e):
    try:
        output_p = document.querySelector("#stpts-output")
        output_p.textContent = 'Reading ...'
        loading_dialog = document.getElementById("loading")
        loading_dialog.showModal()
        worker_config = {
                                "packages": ["numpy"], 
                                "js_modules" : 
                                    {
                                        "main" : {
                                            "https://cdn.jsdelivr.net/npm/three@0.181.2/build/three.module.js": "three"
                                        }
                                        
                                    }
                            }
        worker = PyWorker("./worker.py", type="pyodide", config = worker_config)
        print("before ready")
        # Await for the worker
        await worker.ready
        print("after ready")
        file_input = document.querySelector("#pts-file-upload")
        file_list = file_input.files
        nfiles = len(file_list)
        print(nfiles)
        if nfiles != 0:
            item = file_list.item(0)
            my_bytes: bytes = await get_bytes_from_file(item)
        res = await worker.sync.heavy_compute()
        output_p.textContent = res
        worker.terminate()
        loading_dialog.close()
        
    except Exception as e:
        print(e)

def animate(*args):
    controls.update()
    # Render the scene
    renderer.render(scene, camera)
    # Call the animation loop recursively
    window.requestAnimationFrame(animate_proxy)

animate_proxy = create_proxy(animate)
window.requestAnimationFrame(animate_proxy)
print('done')
if __name__ == "__main__":
    animate()
    add_event_listener(document.getElementById("stpts-submit"), "click", lambda e: asyncio.create_task(on_pts_submit(e)) )