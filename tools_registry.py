from Drawable import BoxDrawable, LinkDrawable, NullDrawable
from Tool import MultipointTool

tools_registry = [
    MultipointTool("Select", NullDrawable),
    MultipointTool("Box", BoxDrawable),
    MultipointTool("Link", LinkDrawable),
]