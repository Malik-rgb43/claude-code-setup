# הסרה

<!-- step: uninstall-01 -->
## uninstall-01 - רואים מה יוסר
```text
python install/setup.py uninstall
```
היא רק מתארת מה היא תסיר.

<!-- step: uninstall-02 -->
## uninstall-02 - מסירים
```text
python install/setup.py uninstall --yes
```
היא מסירה את הבלוק המסומן מ-`~/.claude/CLAUDE.md` (הטקסט שלך נשאר; קובץ `CLAUDE.md` שהכלי הזה יצר ואין בו שום דבר אחר נמחק), את השרת `playwright` ואת התוסף `superpowers` **רק אם הכלי הזה הוסיף אותם**. שרת או תוסף שהיו שם קודם נשארים כמו שהם. הגיבויים ב-`~/.avc/claude-code-setup/backups/` נשמרים; מוחקים את התיקייה בעצמך כשאתה כבר לא צריך אותם. החנות הרשמית של התוספים נשארת מוגדרת (היא של Claude Code עצמו).
