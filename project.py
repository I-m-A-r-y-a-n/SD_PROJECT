from graphviz import Digraph

dot = Digraph(
    name="Unified_Search_ER",
    format="png",
    graph_attr={"rankdir": "TB", "splines": "ortho"},
    node_attr={"fontname": "Helvetica"},
    edge_attr={"fontname": "Helvetica"}
)

# ==============================
# Helper Functions
# ==============================

def entity(name, attributes):
    label = f"<<TABLE BORDER='1' CELLBORDER='0' CELLSPACING='0'>"
    label += f"<TR><TD><B>{name}</B></TD></TR>"
    for attr in attributes:
        label += f"<TR><TD ALIGN='LEFT'>{attr}</TD></TR>"
    label += "</TABLE>>"
    dot.node(name, label=label, shape="plaintext")

def weak_entity(name, attributes):
    label = f"<<TABLE BORDER='2' CELLBORDER='0' CELLSPACING='0'>"
    label += f"<TR><TD><B>{name}</B></TD></TR>"
    for attr in attributes:
        label += f"<TR><TD ALIGN='LEFT'>{attr}</TD></TR>"
    label += "</TABLE>>"
    dot.node(name, label=label, shape="plaintext")

def relationship(name, identifying=False):
    per = "2" if identifying else "1"
    dot.node(name, label=name, shape="diamond", peripheries=per)

def connect(left, rel, right, left_card="", right_card=""):
    dot.edge(left, rel, label=left_card)
    dot.edge(rel, right, label=right_card)

# ==============================
# ENTITIES
# ==============================

entity("USER", [
    "user_id (PK)",
    "email",
    "password_hash",
    "role",
    "status",
    "created_at"
])

entity("CATEGORY", [
    "category_id (PK)",
    "category_name",
    "created_at"
])

entity("TOPIC", [
    "topic_id (PK)",
    "topic_name",
    "category_id (FK)",
    "created_at"
])

entity("SEARCH", [
    "search_id (PK)",
    "query_text",
    "created_at"
])

entity("SOURCE", [
    "source_id (PK)",
    "source_name"
])

entity("CONTENT", [
    "content_id (PK)",
    "title",
    "url",
    "snippet",
    "created_at"
])

weak_entity("BOOKMARK", [
    "bookmark_id (PK)",
    "created_at"
])

weak_entity("FEEDBACK", [
    "feedback_id (PK)",
    "rating",
    "comment",
    "created_at"
])

weak_entity("FLAGGED_CONTENT", [
    "flag_id (PK)",
    "reason",
    "status",
    "created_at"
])

entity("SESSION", [
    "session_id (PK)",
    "last_login"
])

weak_entity("RECOMMENDATION", [
    "rec_id (PK)",
    "reason",
    "shown_at"
])

# ==============================
# RELATIONSHIPS
# ==============================

relationship("PERFORMS")
relationship("CLASSIFIED_AS")
relationship("BELONGS_TO")
relationship("PRODUCES")
relationship("PROVIDED_BY")
relationship("SAVES", identifying=True)
relationship("GIVES_FEEDBACK", identifying=True)
relationship("FLAGS", identifying=True)
relationship("HAS_SESSION")
relationship("RECOMMENDS", identifying=True)

# ==============================
# CONNECTIONS
# ==============================

connect("USER", "PERFORMS", "SEARCH", "1", "N")

connect("SEARCH", "CLASSIFIED_AS", "TOPIC", "N", "1")
connect("TOPIC", "BELONGS_TO", "CATEGORY", "N", "1")

connect("SEARCH", "PRODUCES", "CONTENT", "1", "N")
connect("CONTENT", "PROVIDED_BY", "SOURCE", "N", "1")

connect("USER", "SAVES", "BOOKMARK", "1", "N")
connect("BOOKMARK", "SAVES", "CONTENT", "N", "1")

connect("USER", "GIVES_FEEDBACK", "FEEDBACK", "1", "N")
connect("FEEDBACK", "GIVES_FEEDBACK", "CONTENT", "N", "1")

connect("USER", "FLAGS", "FLAGGED_CONTENT", "1", "N")
connect("FLAGGED_CONTENT", "FLAGS", "CONTENT", "N", "1")

connect("USER", "HAS_SESSION", "SESSION", "1", "1")

connect("USER", "RECOMMENDS", "RECOMMENDATION", "1", "N")
connect("RECOMMENDATION", "RECOMMENDS", "CONTENT", "N", "1")

# ==============================
# RENDER
# ==============================

dot.render("project_er_diagram", cleanup=True)
print("ER diagram generated as project_er_diagram.png")

