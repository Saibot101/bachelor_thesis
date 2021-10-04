import jiwer
import asr_evaluation.asr_evaluation as asr

ground_truth = []
hypothesis = []

transformation = jiwer.Compose([
    jiwer.ToLowerCase(),
    jiwer.RemoveMultipleSpaces(),
    jiwer.RemovePunctuation(),
    jiwer.Strip(),
    jiwer.ExpandCommonEnglishContractions()
])

file = open("cloud_Transcription.txt", "r")
inhalt_ground_truth = []

for _ in range(47):
    inhalt_ground_truth.append(file.readline())

new_list = []
for x in range(0, 46):
    ground_truth.append(inhalt_ground_truth[x])

# Hypothesis
file = open("cloud_azure.txt", "r")
inhalt_hypothesis = []

for _ in range(49):
    inhalt_hypothesis.append(file.readline())

new_list = []
for x in range(2, 48):
    hypothesis.append(inhalt_hypothesis[x])

measures = []
for x in range(len(ground_truth)):
    measures.append(jiwer.compute_measures(ground_truth[x], hypothesis[x], truth_transform=transformation, hypothesis_transform=transformation))


with open('new_txt.txt', 'w') as writer:
    for measure in measures:
        writer.write(str(measure['wer']) + '; ')
        writer.write(str(measure['mer']) + '; ')
        writer.write(str(measure['wil']) + '; ')
        writer.write("\n")
