# ✅ REPLKit — Revue Technique du Système d’Aliases (`@name`)

Cette checklist vise à valider la robustesse, la cohérence et l'ergonomie du système d'alias dans `replkit`.

---

## 1. Fonctionnalité de base

- [x] `.alias @name = expr` crée un alias
- [x] `.alias` affiche la liste des alias
- [x] `.unalias @name` supprime un alias
- [x] L’expansion a lieu avant `eval()`
- [x] L’expansion ne fait pas planter le REPL (erreurs gérées proprement)
- [x] Préfixe `@` obligatoire (évite collisions)
- [x] Les alias sont ajoutés à la complétion (Tab)
- [x] Historique capture `.alias`/`.unalias` comme commandes utilisateur

---

## 2. Sécurité et cohérence

- [x] Rejet des noms d’alias invalides (`@1abc`, `@with space`, etc.)
- [x] Erreur claire si un alias non défini est utilisé (`Alias error: Unknown alias`)
- [x] Avertissement ou rejet lors de la redéfinition d’un alias déjà existant
- [x] Interdiction de contenu vide : `.alias @foo = `
- [ ] Avertissement si l’alias masque une expression équivalente existante (`@foo = @foo`)
- [ ] Vérification future possible de circularité (`@A = @B`, `@B = @A`) – non bloquant pour v1

---

## 3. UX / Interface

- [x] Complétion Tab sur `@name` fonctionne (`readline.set_completer_delims`)
- [x] `.help` liste les commandes `.alias`, `.unalias`
- [x] Message affiché lors d’une redéfinition (`Alias '@x' replaced (was: ...)`)

---

## 4. Intégration et extensibilité

- [x] Préparer interface future pour persistance des alias
- [x] Vérifier le comportement dans les scripts (`--file`, `.load`) :
- [x] alias définis dans fichier fonctionnent
- [x] erreur si fichier contient un alias invalide
- [x] Tester interaction avec l’historique (`!N`) sur lignes contenant des alias

---

## 5. Tests recommandés

Créer test unitaire pour :

- [x] `expand_aliases()` avec plusieurs alias
- [x] Détection alias inconnu
- [ ] Redéfinition
- [ ] Suppression
- [x] Vérifier qu’un alias n’est jamais substitué à l’intérieur d’un nom (ex: `@and` ≠ `@andromede`)
