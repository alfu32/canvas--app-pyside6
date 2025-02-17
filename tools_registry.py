from Drawable import BoxDrawable, LinkDrawable, NullDrawable, SelectDrawable
from Tool import MultipointTool

tools_registry = [
    MultipointTool("Select", SelectDrawable),
    MultipointTool("Box", BoxDrawable),
    MultipointTool("Link", LinkDrawable),
]