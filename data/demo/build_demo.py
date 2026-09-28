"""Build demo files for Oggy Organizer checking."""
from docx import Document
from docx.shared import Pt
from pptx import Presentation
from pptx.util import Inches

OUT = "data/demo"


def para(doc, text, bold=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.bold = bold
    r.font.size = Pt(11)
    return p


def strong_paper():
    doc = Document()
    doc.add_heading("Sparse Attention Retains Accuracy on Citation Graphs", level=1)
    para(doc, "Abstract")
    para(doc, "We study sparse attention for large citation graphs. Our contribution is a pruning schedule that holds accuracy past 80 percent sparsity while cutting training cost by half. Experiments on three public datasets support the claim within the reported settings.")
    para(doc, "Declaration")
    para(doc, "This work is original and has not been submitted elsewhere.")
    para(doc, "Acknowledgements")
    para(doc, "We thank the open-source community for public datasets.")
    para(doc, "1. Introduction")
    para(doc, "Large graph models are costly to train. Prior work prunes weights but rarely reports the sparsity-accuracy trade-off on citation data.")
    para(doc, "2. Literature Review")
    para(doc, "Recent studies cover pruning (Smith et al., 2023, doi:10.1038/nature12373) and attention scaling (Lee et al., 2024, doi:10.1000/xyz123). The research gap is a reproducible schedule evaluated on identical splits.")
    para(doc, "3. Methodology")
    para(doc, "We assume a fixed data split and report validation as the selection criterion. The method prunes 10 percent of weights per round for eight rounds. Assumptions and validation steps are documented so others can reproduce the study.")
    para(doc, "4. Implementation")
    para(doc, "The system is implemented in Python with open libraries. Code availability: https://github.com/example/sparse-attn-demo. Data availability: public splits linked in the repository.")
    para(doc, "5. Testing and Results")
    para(doc, "Figure 1 shows accuracy against sparsity and Table 1 lists per-dataset scores. Results suggest the schedule holds accuracy within one point up to 80 percent sparsity.")
    para(doc, "6. Discussion")
    para(doc, "The results indicate pruning interacts with graph density. Compared with Smith et al., our schedule degrades more slowly. A limitation is that only citation graphs were tested; social graphs may behave differently.")
    para(doc, "7. Conclusion")
    para(doc, "We demonstrate a reproducible pruning schedule for citation graphs and suggest wider evaluation as future work.")
    para(doc, "Conflict of interest: none declared. Ethics approval: not applicable (public data).")
    para(doc, "References")
    para(doc, "[1] Smith, A. et al. Pruning graph models. Journal of Examples, 2023, doi:10.1038/nature12373.")
    para(doc, "[2] Lee, B. et al. Attention scaling. Sample Transactions, 2024, doi:10.1000/xyz123.")
    doc.save(f"{OUT}/demo_paper_strong.docx")


def weak_paper():
    doc = Document()
    doc.add_heading("My Study On Graphs", level=1)
    para(doc, "This paper is very good and presents a very big thing for graphs. Our method always works and proves everything perfectly.")
    para(doc, "Introduction")
    para(doc, "Graphs are a very important thing. A lot of people do a lot of stuff with graphs. This thing is good.")
    para(doc, "Method")
    para(doc, "We did stuff with the data and it was good. The results were very nice.")
    para(doc, "Results")
    para(doc, "Everything was perfect and 100 percent correct, better than all other work forever.")
    para(doc, "Conclusion")
    para(doc, "In conclusion this thing is very very good and everyone should use it always.")
    doc.save(f"{OUT}/demo_paper_weak.docx")


def demo_deck():
    prs = Presentation()
    slides_data = [
        ("Thesis defense: sparse attention", "Name, date", "Welcome everyone, moving to slide 2."),
        ("Problem", "Training is costly; no clear schedule", ""),
        ("Gap in literature", "Nobody reports sparsity trade-offs", "This gap motivates the work."),
        ("Method", "Prune 10 percent per round", ""),
        ("Results", "Holds accuracy to 80 percent sparsity", "Key result, see paper Table 1."),
        ("Claim without source", "Our method cures all graph problems forever", ""),
        ("Evaluation limits", "Only citation graphs tested", ""),
        ("Related work", "Smith 2023, Lee 2024", ""),
        ("Future work", "Social graphs next", ""),
        ("Conclusion", "Reproducible schedule; code online", "Thank you. Questions?"),
    ]
    for title, body, notes in slides_data:
        slide = prs.slides.add_slide(prs.slide_layouts[1])
        slide.shapes.title.text = title
        slide.placeholders[1].text = body
        if notes:
            slide.notes_slide.notes_text_frame.text = notes
    prs.save(f"{OUT}/demo_deck_gaps.pptx")


if __name__ == "__main__":
    strong_paper()
    weak_paper()
    demo_deck()
    print("demo files written")
