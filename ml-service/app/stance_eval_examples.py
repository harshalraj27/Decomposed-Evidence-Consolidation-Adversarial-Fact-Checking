curated_examples = [

    # 1. Proper entailment cases (high-confidence support)
    {
        "claim": "Transformers do not use recurrent neural networks.",
        "evidence": "The Transformer architecture removes recurrence and relies entirely on self-attention.",
        "gold": "support",
        "category": "entailment_high"
    },
    {
        "claim": "Water boils at 100°C at standard atmospheric pressure.",
        "evidence": "At one atmosphere of pressure, water boils at 100 degrees Celsius.",
        "gold": "support",
        "category": "entailment_high"
    },
    {
        "claim": "Smoking increases the risk of lung cancer.",
        "evidence": "Numerous studies show that smoking significantly raises the risk of lung cancer.",
        "gold": "support",
        "category": "entailment_high"
    },
    {
        "claim": "The Earth revolves around the Sun.",
        "evidence": "The Earth orbits the Sun once every year.",
        "gold": "support",
        "category": "entailment_high"
    },
    {
        "claim": "Vaccines help prevent infectious diseases.",
        "evidence": "Vaccination is an effective method for preventing many infectious diseases.",
        "gold": "support",
        "category": "entailment_high"
    },

    # 2. Proper contradiction cases (high-confidence contradict)
    {
        "claim": "Transformers rely on recurrent neural networks.",
        "evidence": "Transformers eliminate recurrence entirely and use only self-attention.",
        "gold": "contradict",
        "category": "contradiction_high"
    },
    {
        "claim": "The Earth is flat.",
        "evidence": "Satellite imagery and astronomical observations show that the Earth is spherical.",
        "gold": "contradict",
        "category": "contradiction_high"
    },
    {
        "claim": "Antibiotics are effective against viral infections.",
        "evidence": "Antibiotics do not work against viruses and are only effective against bacteria.",
        "gold": "contradict",
        "category": "contradiction_high"
    },
    {
        "claim": "Humans can breathe normally in outer space without protection.",
        "evidence": "Outer space lacks oxygen, making unprotected breathing impossible.",
        "gold": "contradict",
        "category": "contradiction_high"
    },
    {
        "claim": "Water freezes at 100°C.",
        "evidence": "Water freezes at 0°C under standard atmospheric conditions.",
        "gold": "contradict",
        "category": "contradiction_high"
    },

    # 3. Neutral dominant cases
    {
        "claim": "Self-attention improves translation quality.",
        "evidence": "The Transformer architecture is based on self-attention mechanisms.",
        "gold": "neutral",
        "category": "neutral"
    },
    {
        "claim": "Climate change increases hurricane frequency.",
        "evidence": "Hurricanes are influenced by ocean temperatures and atmospheric conditions.",
        "gold": "neutral",
        "category": "neutral"
    },
    {
        "claim": "Exercise improves mental health.",
        "evidence": "Exercise has many physical health benefits.",
        "gold": "neutral",
        "category": "neutral"
    },
    {
        "claim": "AI models require large datasets.",
        "evidence": "Deep learning models use neural networks with many parameters.",
        "gold": "neutral",
        "category": "neutral"
    },
    {
        "claim": "Electric cars reduce carbon emissions.",
        "evidence": "Electric vehicles use batteries instead of internal combustion engines.",
        "gold": "neutral",
        "category": "neutral"
    },

    # 4. Lexical overlap traps
    {
        "claim": "The drug is safe for children.",
        "evidence": "The drug is safe for adults when taken as prescribed.",
        "gold": "neutral",
        "category": "lexical_overlap"
    },
    {
        "claim": "The study proves the treatment is effective.",
        "evidence": "The study investigates the effectiveness of the treatment.",
        "gold": "neutral",
        "category": "lexical_overlap"
    },
    {
        "claim": "All patients recovered after treatment.",
        "evidence": "Some patients recovered after receiving the treatment.",
        "gold": "neutral",
        "category": "lexical_overlap"
    },
    {
        "claim": "The algorithm guarantees optimal performance.",
        "evidence": "The algorithm aims to improve performance.",
        "gold": "neutral",
        "category": "lexical_overlap"
    },
    {
        "claim": "The policy reduced unemployment.",
        "evidence": "The policy focuses on employment-related reforms.",
        "gold": "neutral",
        "category": "lexical_overlap"
    },

    # 5. Temporal mismatch
    {
        "claim": "The policy reduced emissions in 2022.",
        "evidence": "The policy aims to reduce emissions over the next decade.",
        "gold": "neutral",
        "category": "temporal_mismatch"
    },
    {
        "claim": "The company made a profit last year.",
        "evidence": "The company plans to become profitable in the future.",
        "gold": "neutral",
        "category": "temporal_mismatch"
    },
    {
        "claim": "The vaccine eliminated the disease globally.",
        "evidence": "The vaccine is expected to reduce disease prevalence.",
        "gold": "neutral",
        "category": "temporal_mismatch"
    },
    {
        "claim": "The experiment confirmed the hypothesis.",
        "evidence": "The experiment is designed to test the hypothesis.",
        "gold": "neutral",
        "category": "temporal_mismatch"
    },
    {
        "claim": "The law was repealed in 2020.",
        "evidence": "The law has been under review since 2019.",
        "gold": "neutral",
        "category": "temporal_mismatch"
    },

    # 6. Myths busted (explicit debunking)
    {
        "claim": "Humans use only 10% of their brains.",
        "evidence": "Brain imaging studies show that most regions of the brain are active.",
        "gold": "contradict",
        "category": "myth_busted"
    },
    {
        "claim": "Vaccines cause autism.",
        "evidence": "Large-scale studies show no link between vaccines and autism.",
        "gold": "contradict",
        "category": "myth_busted"
    },
    {
        "claim": "Lightning never strikes the same place twice.",
        "evidence": "Lightning can strike the same location multiple times.",
        "gold": "contradict",
        "category": "myth_busted"
    },
    {
        "claim": "Sugar causes hyperactivity in children.",
        "evidence": "Controlled studies find no consistent link between sugar intake and hyperactivity.",
        "gold": "contradict",
        "category": "myth_busted"
    },
    {
        "claim": "Goldfish have a three-second memory.",
        "evidence": "Experiments show goldfish can remember tasks for months.",
        "gold": "contradict",
        "category": "myth_busted"
    },

    # 7. Non-busted myths / unresolved
    {
        "claim": "Aliens have visited Earth.",
        "evidence": "There is ongoing research into unidentified aerial phenomena.",
        "gold": "neutral",
        "category": "unresolved_myth"
    },
    {
        "claim": "Dreams predict future events.",
        "evidence": "Dreams occur during specific sleep stages.",
        "gold": "neutral",
        "category": "unresolved_myth"
    },
    {
        "claim": "Certain foods significantly boost intelligence.",
        "evidence": "Nutrition plays a role in brain health.",
        "gold": "neutral",
        "category": "unresolved_myth"
    },
    {
        "claim": "Some people have psychic abilities.",
        "evidence": "Human perception is influenced by cognitive biases.",
        "gold": "neutral",
        "category": "unresolved_myth"
    },
    {
        "claim": "Astrology determines personality traits.",
        "evidence": "Astrology is a belief system practiced across cultures.",
        "gold": "neutral",
        "category": "unresolved_myth"
    },

    # 8. Debunked scientific claims
    {
        "claim": "Cold fusion has been reliably demonstrated in laboratories.",
        "evidence": "Attempts to replicate cold fusion experiments have failed.",
        "gold": "contradict",
        "category": "debunked_science"
    },
    {
        "claim": "The Earth is the center of the universe.",
        "evidence": "Astronomical observations support a heliocentric and expanding universe.",
        "gold": "contradict",
        "category": "debunked_science"
    },
    {
        "claim": "Phrenology accurately measures intelligence.",
        "evidence": "Phrenology is considered a pseudoscience with no empirical support.",
        "gold": "contradict",
        "category": "debunked_science"
    },
    {
        "claim": "Heavier objects fall faster than lighter ones in a vacuum.",
        "evidence": "Physics experiments show all objects fall at the same rate in a vacuum.",
        "gold": "contradict",
        "category": "debunked_science"
    },
    {
        "claim": "The Sun revolves around the Earth.",
        "evidence": "Observations show the Earth orbits the Sun.",
        "gold": "contradict",
        "category": "debunked_science"
    },

    # 9. Quantifier & scope mismatch
    {
        "claim": "All birds can fly.",
        "evidence": "Some birds, such as penguins, cannot fly.",
        "gold": "contradict",
        "category": "quantifier_scope"
    },
    {
        "claim": "Some vaccines cause side effects.",
        "evidence": "Vaccines are generally safe for the population.",
        "gold": "neutral",
        "category": "quantifier_scope"
    },
    {
        "claim": "No students failed the exam.",
        "evidence": "Several students failed the exam.",
        "gold": "contradict",
        "category": "quantifier_scope"
    },
    {
        "claim": "Most people like coffee.",
        "evidence": "Coffee is a popular beverage worldwide.",
        "gold": "neutral",
        "category": "quantifier_scope"
    },
    {
        "claim": "Every algorithm benefits from more data.",
        "evidence": "Some algorithms perform worse with noisy data.",
        "gold": "neutral",
        "category": "quantifier_scope"
    },

    # 10. Scientific hedging & uncertainty
    {
        "claim": "The drug cures the disease.",
        "evidence": "The drug may help reduce symptoms in some patients.",
        "gold": "neutral",
        "category": "scientific_hedging"
    },
    {
        "claim": "The model guarantees perfect accuracy.",
        "evidence": "The model performs well on benchmark datasets.",
        "gold": "neutral",
        "category": "scientific_hedging"
    },
    {
        "claim": "Climate change will certainly cause mass extinction.",
        "evidence": "Climate change poses significant risks to biodiversity.",
        "gold": "neutral",
        "category": "scientific_hedging"
    },
    {
        "claim": "The theory has been conclusively proven.",
        "evidence": "The theory is supported by experimental evidence.",
        "gold": "neutral",
        "category": "scientific_hedging"
    },
    {
        "claim": "The treatment is completely safe.",
        "evidence": "The treatment has been shown to be generally safe.",
        "gold": "neutral",
        "category": "scientific_hedging"
    },
]