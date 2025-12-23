import re
from dataclasses import dataclass

CONJ_SPLIT = re.compile(r"\s+(and|but|or|while|whereas)\s+", re.I)
CONJ_WORDS = {"and", "but", "or", "while", "whereas"}
PRONOUNS = {"he", "she", "it", "they", "we", "i", "you", "this", "that", "these", "those", "who", "which"}
ADVERBS = {"however", "moreover", "furthermore", "therefore", "thus", "hence", "consequently", "nevertheless"}


@dataclass
class Subclaim:
    id: int
    text: str
    type: str
    source_claim: str

def normalize(text):
    text = text.strip()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("'", "'")
    return text


def valid(text):
    return 5 <= len(text) <= 200


def infer_type(text):
    t = text.lower()
    if " than " in t or any(x in t for x in ["faster", "slower", "better", "worse", "more", "less"]):
        return "COMPARATIVE"
    if any(x in t for x in ["because", "due to", "leads to", "results in", "causes", "since", "therefore"]):
        return "CAUSAL"
    if any(x in t for x in ["is defined as", "refers to", "means that"]):
        return "DEFINITION"
    if any(x in t for x in ["i think", "we believe", "arguably", "in my opinion", "likely", "probably"]):
        return "OPINION"
    return "FACTUAL"


def extract_suffix(text):
    m = re.search(r"(than\s+.+)$", text, re.I)
    return m.group(1) if m else ""


def extract_subject_verb(text):
    patterns = [
        r"^([A-Z][^,\.]+?(?:\s+(?:is|are|was|were|has|have|had|can|could|will|would|should|may|might|must|do|does|did))\s+)",
        r"^([A-Z][^,\.]+?\s+(?:is|are|was|were)\s+)",
        r"^([A-Z][^,\.]+?\s+[a-z]+s\s+)",
        r"^([A-Z][^,\.]+?\s+[a-z]+ed\s+)",
    ]

    for pattern in patterns:
        m = re.match(pattern, text)
        if m:
            subject_verb = m.group(1).strip()
            words = subject_verb.split()
            verb = words[-1]
            return subject_verb, verb

    words = text.split()
    if len(words) >= 2:
        for i, word in enumerate(words[1:], 1):
            if word.lower() in {"is", "are", "was", "were", "has", "have", "had", "can", "will", "would", "should"}:
                subject_verb = " ".join(words[:i + 1])
                return subject_verb, word

    noun_pattern = r"^([A-Z][a-z]*(?:\s+[a-z]+)*?\s+(?:[a-z]+s|models?|systems?|people|users?|data|methods?|algorithms?|programs?))(?:\s+([a-z]+))"
    m = re.match(noun_pattern, text)
    if m:
        return m.group(1).strip(), None

    if len(words) >= 3:
        potential_subject = " ".join(words[:-1])
        if len(potential_subject.split()) >= 2:
            return potential_subject, None

    return None, None


def is_comparative_fragment(text):
    t = text.lower()
    comp_words = ["faster", "slower", "better", "worse", "more", "less", "easier", "harder", "larger", "smaller",
                  "higher", "lower", "greater", "cheaper", "costlier"]
    return any(word in t for word in comp_words)


def is_complete_clause(text):
    words = text.split()
    if len(words) < 2:
        return False

    first_word = words[0].lower()

    if first_word in PRONOUNS:
        return True

    if first_word in ADVERBS:
        return True

    if is_comparative_fragment(text) and " than " not in text.lower():
        return False

    if words[0][0].isupper() and first_word not in CONJ_WORDS:
        common_determiners = {"the", "a", "an", "some", "many", "most", "all", "each", "every"}
        if len(words) >= 3 and words[1].lower() not in common_determiners:
            return True

    return False


def needs_subject(text):
    text = text.strip()
    words = text.split()
    if not words:
        return False

    first_word = words[0].lower()

    common_verbs = {"is", "are", "was", "were", "has", "have", "had", "can", "will", "would", "does", "did",
                    "scale", "scales", "perform", "performs", "work", "works", "fail", "fails", "succeed", "succeeds",
                    "run", "runs", "execute", "executes"}

    if first_word in common_verbs:
        return True

    if first_word in {"more", "less", "better", "worse", "faster", "slower"}:
        return True

    verb_patterns = [r"^[a-z]+s\s", r"^[a-z]+ed\s", r"^[a-z]+ing\s",
                     r"^[a-z]+\s+(?:well|poorly|better|worse|quickly|slowly)"]

    for pattern in verb_patterns:
        if re.match(pattern, text):
            return True

    adjective_patterns = [r"^(?:more|less|very|extremely|highly)\s+[a-z]+", r"^[a-z]+er\s+", r"^[a-z]+est\s+"]

    for pattern in adjective_patterns:
        if re.match(pattern, text):
            return True

    return False


def has_verb_mismatch(subject_verb, fragment):
    if not subject_verb:
        return False

    sv_words = subject_verb.split()
    if not sv_words:
        return False

    verb = sv_words[-1].lower()
    frag_words = fragment.split()
    if not frag_words:
        return False

    first_word = frag_words[0].lower()

    if first_word in {"more", "less", "better", "worse", "faster", "slower"}:
        return False

    if verb in {"is", "are", "was", "were"} and first_word not in {"is", "are", "was", "were", "being"}:
        if not any(first_word.startswith(prefix) for prefix in ["be", "is", "are", "was", "were"]):
            return True

    return False


def split_on_conjunctions_and_commas(text):
    text = re.sub(r",\s+(and|but|or)\s+", r" \1 ", text)
    text = re.sub(r",\s+", " and ", text)

    raw = CONJ_SPLIT.split(text)
    return raw


def rule_decompose(claim):
    claim = normalize(claim)
    suffix = extract_suffix(claim)
    subject_verb, verb = extract_subject_verb(claim)
    is_claim_comparative = infer_type(claim) == "COMPARATIVE"

    raw = split_on_conjunctions_and_commas(claim)
    parts = []

    for p in raw:
        p = p.strip()
        if not p or p.lower() in CONJ_WORDS:
            continue

        if is_complete_clause(p):
            if valid(p):
                parts.append(p)
            continue

        if subject_verb and needs_subject(p):
            if not has_verb_mismatch(subject_verb, p):
                p = f"{subject_verb} {p}"

        if suffix and " than " not in p.lower() and is_claim_comparative and is_comparative_fragment(p):
            p = f"{p} {suffix}"

        if valid(p):
            parts.append(p)

    subclaims = []
    for i, p in enumerate(parts):
        subclaims.append(
            Subclaim(
                id=i,
                text=p,
                type=infer_type(p),
                source_claim=claim
            )
        )

    if not subclaims:
        subclaims.append(Subclaim(0, claim, infer_type(claim), claim))

    return subclaims