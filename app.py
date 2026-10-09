"""
File Manager - a Streamlit web app for basic file handling.

Create, read, edit, append, rename, download and delete text files
inside a workspace folder.

Run with:  streamlit run app.py
"""

from datetime import datetime
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="File Manager", page_icon="📁", layout="wide")

WORKSPACE = Path(__file__).parent / "workspace"
WORKSPACE.mkdir(exist_ok=True)

ICONS = {
    ".txt": "📄", ".md": "📝", ".py": "🐍", ".json": "🧾", ".csv": "📊",
    ".html": "🌐", ".css": "🎨", ".js": "⚡", ".log": "📋",
}


# ---------- Helpers ----------
def valid_name(name: str) -> bool:
    """Reject empty names and anything containing a path (e.g. ../x)."""
    return bool(name) and Path(name).name == name and name not in (".", "..")


def list_files() -> list[str]:
    return sorted(p.name for p in WORKSPACE.iterdir() if p.is_file())


def icon_for(name: str) -> str:
    return ICONS.get(Path(name).suffix.lower(), "📄")


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{int(size)} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024
    return f"{num_bytes} B"


def flash(kind: str, message: str) -> None:
    """Store a message to show after the next rerun (success / error / warning)."""
    st.session_state["flash"] = (kind, message)


def select(name: str | None) -> None:
    """Choose which file is open; applied at the top of the next run."""
    st.session_state["pending_select"] = name


def create_file(name: str) -> None:
    name = name.strip()
    if not valid_name(name):
        flash("error", "Please enter a valid file name.")
        return
    if "." not in name:
        name += ".txt"
    path = WORKSPACE / name
    if path.exists():
        flash("error", f"'{name}' already exists.")
        return
    try:
        path.touch()
    except OSError as e:
        flash("error", f"Could not create file: {e}")
        return
    select(name)
    flash("success", f"Created {name}")


# ---------- Styling ----------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {font-family: 'Inter', sans-serif;}
    #MainMenu, footer {visibility: hidden;}
    .block-container {padding-top: 1.6rem; max-width: 1100px;}

    /* Hero banner */
    .hero {
        background: linear-gradient(135deg, #7c5cff 0%, #4f8cff 55%, #22d3ee 100%);
        border-radius: 18px; padding: 1.6rem 2rem; margin-bottom: 1.2rem;
        box-shadow: 0 10px 30px rgba(124, 92, 255, .25);
    }
    .hero h1 {color: #fff; margin: 0; padding: 0; font-size: 2rem; font-weight: 700;}
    .hero p {color: rgba(255,255,255,.88); margin: .35rem 0 0; font-size: 1rem;}

    /* Stat cards */
    [data-testid="stMetric"] {
        background: #171a24; border: 1px solid #262a38; border-radius: 14px;
        padding: 14px 18px;
    }
    [data-testid="stMetricLabel"] {color: #8b8fa8;}
    [data-testid="stMetricValue"] {font-size: 1.5rem; font-weight: 600;}

    /* Feature cards on the welcome screen */
    .card {
        background: #171a24; border: 1px solid #262a38; border-radius: 14px;
        padding: 1.2rem 1.3rem; height: 100%;
    }
    .card h3 {margin: 0 0 .4rem; font-size: 1.05rem;}
    .card p {margin: 0; color: #8b8fa8; font-size: .92rem;}

    /* Buttons */
    div.stButton > button, div.stDownloadButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        border-radius: 10px; font-weight: 600; border: 1px solid #2d3142;
        transition: all .15s ease;
    }
    div.stButton > button:hover, div.stDownloadButton > button:hover {
        transform: translateY(-1px); border-color: #7c5cff;
    }
    button[kind="primary"], button[kind="primaryFormSubmit"] {
        background: linear-gradient(135deg, #7c5cff, #4f8cff) !important;
        border: none !important; color: #fff !important;
    }

    /* Editor */
    textarea {
        font-family: 'JetBrains Mono', monospace !important; font-size: .92rem !important;
        border-radius: 12px !important;
    }

    /* Tabs */
    button[data-baseweb="tab"] {font-weight: 600; padding: 10px 16px;}

    /* Sidebar */
    section[data-testid="stSidebar"] {border-right: 1px solid #262a38;}
    section[data-testid="stSidebar"] h1 {font-size: 1.4rem; font-weight: 700;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Apply a pending selection BEFORE the radio widget is created
if "pending_select" in st.session_state:
    st.session_state["selected"] = st.session_state.pop("pending_select")

# ---------- Sidebar ----------
with st.sidebar:
    st.title("📁 Files")

    with st.form("new_file_form", clear_on_submit=True):
        new_name = st.text_input("New file", placeholder="notes.txt")
        if st.form_submit_button("➕ Create file", type="primary", use_container_width=True):
            create_file(new_name)
            st.rerun()

    st.divider()
    search = st.text_input("Search", placeholder="🔍 Filter files...", label_visibility="collapsed")
    files = list_files()
    shown = [f for f in files if search.lower().strip() in f.lower()]

    if st.session_state.get("selected") not in shown:
        st.session_state.pop("selected", None)

    if shown:
        st.radio(
            "Files", shown, key="selected",
            format_func=lambda n: f"{icon_for(n)}  {n}",
            label_visibility="collapsed",
        )
    else:
        st.info("No files yet. Create one above." if not files else "No matches.")

    st.caption(f"{len(files)} file(s) in `{WORKSPACE.name}/`")

# ---------- Header ----------
st.markdown(
    """
    <div class="hero">
        <h1>📁 File Manager</h1>
        <p>Create, edit and organize text files, right from your browser.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "flash" in st.session_state:
    kind, message = st.session_state.pop("flash")
    getattr(st, kind)(message)

selected = st.session_state.get("selected")
total_size = sum(p.stat().st_size for p in WORKSPACE.iterdir() if p.is_file())

# ---------- Welcome screen ----------
if not selected:
    c1, c2, c3 = st.columns(3)
    c1.metric("Files", len(files))
    c2.metric("Total size", human_size(total_size))
    c3.metric("Workspace", WORKSPACE.name + "/")

    st.write("")
    st.subheader("What you can do")
    f1, f2, f3 = st.columns(3)
    f1.markdown(
        '<div class="card"><h3>✏️ Create &amp; edit</h3>'
        "<p>Make new files and edit them in a built-in editor with live counts.</p></div>",
        unsafe_allow_html=True,
    )
    f2.markdown(
        '<div class="card"><h3>🏷️ Rename &amp; append</h3>'
        "<p>Rename files safely or add text to the end without opening the editor.</p></div>",
        unsafe_allow_html=True,
    )
    f3.markdown(
        '<div class="card"><h3>🗑️ Delete &amp; download</h3>'
        "<p>Download any file, or delete it after a confirmation step.</p></div>",
        unsafe_allow_html=True,
    )
    st.write("")
    st.info("👈 Create a file from the sidebar, or pick one to get started.")
    st.stop()

# ---------- File view ----------
path = WORKSPACE / selected
if not path.exists():
    flash("warning", "That file no longer exists.")
    select(None)
    st.rerun()

try:
    content = path.read_text(encoding="utf-8")
except UnicodeDecodeError:
    st.error("This doesn't look like a text file, so it can't be opened here.")
    st.stop()
except OSError as e:
    st.error(f"Could not read file: {e}")
    st.stop()

# `rev` changes whenever the file is changed outside the editor,
# which forces the text area to reload its content.
rev = st.session_state.get("rev", 0)

stat = path.stat()
line_count = content.count("\n") + 1 if content else 0
m1, m2, m3, m4 = st.columns(4)
m1.metric("Files", len(files))
m2.metric("File size", human_size(stat.st_size))
m3.metric("Lines", line_count)
m4.metric("Modified", datetime.fromtimestamp(stat.st_mtime).strftime("%d %b, %H:%M"))

st.write("")
st.subheader(f"{icon_for(selected)}  {selected}")

VIEWS = ["✏️ Edit", "➕ Append", "🏷️ Rename", "🗑️ Delete"]
# A keyed radio remembers the chosen view across reruns (st.tabs does not).
view = st.radio("Action", VIEWS, key="view", horizontal=True, label_visibility="collapsed")
st.write("")

if view == "✏️ Edit":
    text = st.text_area(
        "Content",
        value=content,
        height=360,
        key=f"editor-{selected}-{rev}",
        label_visibility="collapsed",
        placeholder="Start typing...",
    )
    st.caption(
        f"{(text.count(chr(10)) + 1) if text else 0} lines · {len(text)} characters"
        + ("  ·  ⚠️ unsaved changes" if text != content else "")
    )

    col_save, col_dl, _ = st.columns([1, 1, 3])
    if col_save.button("💾 Save", type="primary", use_container_width=True):
        try:
            path.write_text(text, encoding="utf-8")
            flash("success", "Saved.")
            st.rerun()
        except OSError as e:
            st.error(f"Could not save: {e}")
    col_dl.download_button(
        "⬇️ Download", data=text, file_name=selected, use_container_width=True
    )

elif view == "➕ Append":
    extra = st.text_area(
        "Text to add at the end of the file",
        key=f"append-{selected}-{rev}",
        height=140,
    )
    if st.button("➕ Append text", type="primary"):
        if not extra:
            st.warning("Type something to append first.")
        else:
            try:
                prefix = "\n" if content and not content.endswith("\n") else ""
                with open(path, "a", encoding="utf-8") as f:
                    f.write(prefix + extra + "\n")
            except OSError as e:
                st.error(f"Could not append: {e}")
            else:
                st.session_state["rev"] = rev + 1
                flash("success", "Text appended.")
                st.rerun()

elif view == "🏷️ Rename":
    new_file_name = st.text_input("New file name", value=selected, key=f"rename-{selected}")
    if st.button("🏷️ Rename file", type="primary"):
        new_file_name = new_file_name.strip()
        if not valid_name(new_file_name):
            st.error("Please enter a valid file name.")
        elif new_file_name == selected:
            st.info("That's already the file's name.")
        elif (WORKSPACE / new_file_name).exists():
            st.error(f"'{new_file_name}' already exists.")
        else:
            try:
                path.rename(WORKSPACE / new_file_name)
            except OSError as e:
                st.error(f"Could not rename: {e}")
            else:
                select(new_file_name)
                flash("success", f"Renamed to {new_file_name}")
                st.rerun()

else:  # Delete
    st.warning(f"This will permanently delete **{selected}**.")
    sure = st.checkbox("Yes, I'm sure", key=f"sure-{selected}")
    if st.button("🗑️ Delete file", disabled=not sure):
        try:
            path.unlink()
        except OSError as e:
            st.error(f"Could not delete: {e}")
        else:
            select(None)
            flash("success", f"Deleted {selected}")
            st.rerun()