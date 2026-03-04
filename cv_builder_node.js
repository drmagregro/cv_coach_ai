const fs = require('fs');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  LevelFormat, BorderStyle
} = require('docx');

const data = JSON.parse(fs.readFileSync('/tmp/cv_data.json', 'utf8'));

function sectionTitle(text) {
  return new Paragraph({
    children: [new TextRun({ text: text.toUpperCase(), bold: true, size: 22, font: "Arial", color: "1a1a1a" })],
    spacing: { before: 280, after: 60 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "1a1a1a", space: 1 } }
  });
}

function bulletLine(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    children: [new TextRun({ text, size: 20, font: "Arial" })]
  });
}

function spacer() {
  return new Paragraph({ children: [new TextRun("")], spacing: { after: 80 } });
}

const children = [];

// NOM
children.push(new Paragraph({
  alignment: AlignmentType.LEFT,
  children: [new TextRun({ text: data.nom || "", bold: true, size: 36, font: "Arial", color: "1a1a1a" })]
}));

// TITRE
if (data.titre) {
  children.push(new Paragraph({
    children: [new TextRun({ text: data.titre, size: 24, font: "Arial", color: "555555", italics: true })],
    spacing: { after: 80 }
  }));
}

// CONTACT
const c = data.contact || {};
const contactParts = [c.email, c.telephone, c.localisation, c.linkedin].filter(Boolean);
children.push(new Paragraph({
  children: [new TextRun({ text: contactParts.join("  |  "), size: 18, font: "Arial", color: "555555" })],
  spacing: { after: 160 }
}));

// PROFIL
if (data.profil) {
  children.push(sectionTitle("Profil"));
  children.push(new Paragraph({
    children: [new TextRun({ text: data.profil, size: 20, font: "Arial" })],
    spacing: { after: 120 }
  }));
}

// EXPERIENCE
if (data.experience && data.experience.length > 0) {
  children.push(sectionTitle("Expérience professionnelle"));
  data.experience.forEach(exp => {
    children.push(new Paragraph({
      children: [
        new TextRun({ text: exp.poste || "", bold: true, size: 22, font: "Arial" }),
        new TextRun({ text: "  —  " + (exp.entreprise || ""), size: 22, font: "Arial", color: "333333" }),
      ],
      spacing: { before: 140, after: 40 }
    }));
    if (exp.periode) {
      children.push(new Paragraph({
        children: [new TextRun({ text: exp.periode, size: 18, font: "Arial", color: "888888", italics: true })],
        spacing: { after: 60 }
      }));
    }
    (exp.missions || []).forEach(m => children.push(bulletLine(m)));
    children.push(spacer());
  });
}

// FORMATION
if (data.formation && data.formation.length > 0) {
  children.push(sectionTitle("Formation"));
  data.formation.forEach(f => {
    const annee = f.annee ? "  (" + f.annee + ")" : "";
    children.push(new Paragraph({
      children: [
        new TextRun({ text: f.diplome || "", bold: true, size: 22, font: "Arial" }),
        new TextRun({ text: "  —  " + (f.etablissement || "") + annee, size: 20, font: "Arial", color: "555555" })
      ],
      spacing: { before: 100, after: 60 }
    }));
  });
  children.push(spacer());
}

// COMPETENCES
const comp = data.competences || {};
if ((comp.techniques && comp.techniques.length) || (comp.soft_skills && comp.soft_skills.length) || (comp.langues && comp.langues.length)) {
  children.push(sectionTitle("Compétences"));
  if (comp.techniques && comp.techniques.length) {
    children.push(new Paragraph({
      children: [
        new TextRun({ text: "Techniques : ", bold: true, size: 20, font: "Arial" }),
        new TextRun({ text: comp.techniques.join(", "), size: 20, font: "Arial" })
      ],
      spacing: { before: 100, after: 60 }
    }));
  }
  if (comp.soft_skills && comp.soft_skills.length) {
    children.push(new Paragraph({
      children: [
        new TextRun({ text: "Qualités : ", bold: true, size: 20, font: "Arial" }),
        new TextRun({ text: comp.soft_skills.join(", "), size: 20, font: "Arial" })
      ],
      spacing: { after: 60 }
    }));
  }
  if (comp.langues && comp.langues.length) {
    children.push(new Paragraph({
      children: [
        new TextRun({ text: "Langues : ", bold: true, size: 20, font: "Arial" }),
        new TextRun({ text: comp.langues.join(", "), size: 20, font: "Arial" })
      ],
      spacing: { after: 60 }
    }));
  }
  children.push(spacer());
}

// CERTIFICATIONS
if (data.certifications && data.certifications.length > 0) {
  children.push(sectionTitle("Certifications"));
  data.certifications.forEach(cert => children.push(bulletLine(cert)));
  children.push(spacer());
}

// PROJETS
if (data.projets && data.projets.length > 0) {
  children.push(sectionTitle("Projets"));
  data.projets.forEach(p => {
    children.push(new Paragraph({
      children: [new TextRun({ text: p.nom || "", bold: true, size: 20, font: "Arial" })]
    }));
    if (p.description) {
      children.push(new Paragraph({
        children: [new TextRun({ text: p.description, size: 20, font: "Arial", color: "444444" })],
        spacing: { after: 80 }
      }));
    }
  });
}

const doc = new Document({
  numbering: {
    config: [{
      reference: "bullets",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2013",
        alignment: AlignmentType.LEFT,
        style: { paragraph: { indent: { left: 360, hanging: 240 } } } }]
    }]
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 20 } } }
  },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1080, right: 1080, bottom: 1080, left: 1080 }
      }
    },
    children
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync('/tmp/cv_ats.docx', buf);
  console.log('OK');
});