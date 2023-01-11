kubectl port-forward deployment/corenlp                                4080:80 -n chirpycardinal &
kubectl port-forward deployment/dialogact                              4081:80 -n chirpycardinal &
kubectl port-forward deployment/g2p                                    4082:80 -n chirpycardinal &
kubectl port-forward deployment/questionclassifier                     4084:80 -n chirpycardinal &
kubectl port-forward deployment/entitylinker                           4086:80 -n chirpycardinal &
kubectl port-forward deployment/blenderbot                             4087:80 -n chirpycardinal &
kubectl port-forward deployment/stanfordnlp                            4089:80 -n chirpycardinal
# kubectl port-forward deployment/postgresql                             5432:5432 -n chirpycardinal
