from Drawable import SelectDrawable
from Tool import MultipointModifierTool, BoxDrawableTool, OneClickTool
from Drawable import LinkDrawable
from Tool import MultipointTool

def save(m:'ModelDrawable'):
    print(f"intercepted model")
    # for d in m.get_all_linear():
    #     print(d)
    m.ask_save_file()

def load(m:'ModelDrawable'):
    print(f"intercepted model")
    # for d in m.get_all_linear():
    #     print(d)
    m.ask_open_file()

select_tool=MultipointModifierTool("Select", SelectDrawable)
drawable_box_tool=BoxDrawableTool()
link_box_tool=MultipointTool("Link", LinkDrawable)
save_model_json=OneClickTool("Save",save)
load_model_json=OneClickTool("Load",load)
