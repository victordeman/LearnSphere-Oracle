"""
Question Classifier Module
Classifies survey questions into MBTI and ILS dimensions for scoring.
"""

class QuestionClassifier:
    def __init__(self):
        # Dictionary mapping dimensions to lists of questions (from survey text)
        self.question_map = {
            # MBTI: E/I (social interaction, attention)
            "Extrovert_Introvert": [
                "If you need to approach someone in high authority for a favor, would you prefer to ask them:",
                "How quickly are you on the dance floor at a social function?",
                "Would you describe yourself as a leader or a follower?",
                "What would be your reaction if someone asked you to sell some raffle tickets for charity?",
                "Do you think people see you as a fun person?",
                "What would be your reaction if the position of chair suddenly became vacant on a committee on which you were sitting?",
                "How often do you let your opinions be known?",
                "Do you enjoy being the centre of attention?",
                "Which of the following words would you say is the most applicable to you?",
                "Do you enjoy making small talk at buffet lunches?",
                "Do you prefer to discuss things face-to-face or over the telephone?",
                "Would you go out of your way to meet ‘the right people’ ?",
                "Do you enjoy performing your party piece at Christmas parties and other occasions?",
                "Would you appear naked on a charity calendar?",
                "Do you ever run out of things to say when talking to someone you have just met?"
            ],
            # MBTI: T/F (empathy vs logic)
            "Thinking_Feeling": [
                "I always seem to find myself rooting for the underdog.",
                "I admire people who are prepared to admit they were wrong.",
                "I feel great sympathy for street beggars.",
                "I believe that there is such a thing as love at first sight.",
                "I am turned off completely by vulgar jokes and sexual innuendo.",
                "After a serious argument with my partner all I want to do is make up as quickly as possible",
                "If someone does me a bad turn I don’t waste time thinking of revenge.",
                "My heart rules my head more than my head rules my heart.",
                "I would put in a good word for a work colleague who I thought deserved my support.",
                "I detest watching movies that contain excessive violence.",
                "I feel very sorry for people who always seem to be the butt of other people’s jokes.",
                "I would encourage anyone to talk over their troubles with me.",
                "I have always ensured that I put aside some quality time to spend with my partner.",
                "I always buy my partner a card or present on St.Valentine’s Day.",
                "On occasions my eyes have filled up with tears when watching a movie, be it happy or sad.",
                "I would always go out of my way to help someone who is going through an emotional trauma.",
                "I would find it extremely difficult to tell anyone some real home truths.",
                "I have never found it difficult to forgive and forget.",
                "I like stroking cats and/or dogs.",
                "I find it difficult to say ‘No’ when asked for a favor.",
                "I am as supportive of others as I am ambitious for my own aspirations.",
                "I often feel happy for other people.",
                "People should be much more concerned about other people."
            ],
            # MBTI: S/N, J/P, and other (grouped by sections like Success/Risk, Optimist/Pessimist, etc.)
            "Sensing_Intuitive": [ # Practical vs imaginative, risk
                "Getting on in business requires ruthlessness.",
                "My success is due to my ability to think strategically while overseeing day-to-day activities.",
                "My success is due to my full understanding of the marketplace and competitors’ trends.",
                "The higher the risk, the higher the potential return.",
                "Regulations stifle creativity.",
                "Success belongs to the bold."
                # Add more from sections
            ],
            "Judging_Perceiving": [
                "I believe that superstitious beliefs, e.g. ‘breaking a mirror brings 7 years’ bad luck’, are bunkum.",
                "I never even notice the fire regulations when staying in a hotel, let alone read them.",
                "You must speculate to accumulate.",
                "When one door closes another one always opens.",
                "I am constantly on the lookout for opportunities to move on to new and exciting ventures.",
                "Every dog has his day.",
                "In the long run, things always turn out for the better.",
                "I fully expect that one day I will be a big winner on the lottery or premium bonds.",
                "Things are never quite as bad as they appear.",
                "If at first you don’t succeed, you should try, try and try again.",
                "It is always possible to find a silver lining to every cloud if you look hard enough and long enough.",
                "Ultimately, good will always triumph over evil.",
                "Something positive always comes from adversity.",
                "I am all in favor of taking calculated risks."
                # Add managing and communicating
            ],
            # ILS dimensions (infer from questions, e.g., visual/verbal from communication prefs)
            "Active_Reflective": [ # Group vs solitary
                "To manage people well you have to get fully involved in the detail.",
                "Above all else, good management includes trusting people to do the job.",
                "I feel happiest when I can implement defined regulatory processes."
            ],
            "Visual_Verbal": [
                "Do you prefer to discuss things face-to-face or over the telephone?",
                "I am happiest producing written material and much prefer that role to one that involves presenting an argument orally."
            ],
            "Sequential_Global": [
                "My success is due to my ability to think laterally and outside of the box.",
                "I wish I could more often make novel links between previously unconnected issues."
            ]
            # Add more as needed; this is a starter mapping
        }

    def classify_question(self, question_text):
        for dimension, questions in self.question_map.items():
            if question_text in questions:
                return dimension
        return "Unclassified"

    def score_from_answers(self, questions, answers):
        # Placeholder: Aggregate scores per dimension based on answers (e.g., yes/no or 1-5 scale)
        scores = {dim: 0 for dim in self.question_map}
        for q, a in zip(questions, answers):
            dim = self.classify_question(q)
            if dim != "Unclassified":
                scores[dim] += a  # Assume numeric answers; adjust for scale
        return scores
