import ListaVagas from "./ListaVagas";
import { AREAS } from "../config/areas";

export default function VagasDev() {
  return <ListaVagas area={AREAS.dev} />;
}
