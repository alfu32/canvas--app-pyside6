from Drawable import BoxDrawable, LinkDrawable
from Tool import MultipointTool

tools_registry = [
    MultipointTool("Box", BoxDrawable),
    MultipointTool("Link", LinkDrawable),
]