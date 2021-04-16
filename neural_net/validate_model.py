import preprocessing
import validation

string = "../model_configurations/tokenizer_configurations/preprocessing-config-no-keyw-no-keyw"
#string = "../saved_preprocessing_configuration_filtered"

# validate the model against the reference labels
print("Validating the model against true labels of FP dataset")
validation.validate_model("../saved-model", preprocessing.Preprocessing().load(string),
                          "../validation_datasets/validation_dataset_control_pos",
               "../validation_datasets/validation_dataset_control_pos_annonated")

print("Validating the model against true labels of COMPLETE dataset")
validation.validate_model("../saved-model", preprocessing.Preprocessing().load(string),
                          "../validation_datasets/final_validation_dataset",
               "../validation_datasets/final_validation_dataset_annotated")