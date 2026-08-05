#pragma once

#include <JuceHeader.h>
#include <functional>
#include <vector>
#include "SchurLookAndFeel.h"

namespace schurUi
{

//==============================================================================
/** Shared plugin top bar, matching the house style: a flat panel strip with a
    bottom hairline, the plugin name on the left, a centred preset pill
    (◀ name ▾ ▶), and accent-highlighted tab buttons on the right. Custom-painted
    with its own hit-testing so every element shares one look. */
class PluginTopBar : public juce::Component
{
public:
    static constexpr int kHeight = 44;

    PluginTopBar() { setMouseCursor (juce::MouseCursor::PointingHandCursor); }

    void setTitle (juce::String t)    { title = std::move (t); repaint(); }
    void setSubtitle (juce::String s) { subtitle = std::move (s); repaint(); }
    void setDrawBackground (bool b)   { drawBg = b; repaint(); }

    // ---- preset wiring ----
    std::function<int()>                presetCount;
    std::function<int()>                presetIndex;
    std::function<juce::String (int)>   presetName;
    std::function<void (int)>           selectPreset;

    // ---- right-aligned tabs (added left→right) ----
    struct Tab { juce::String label; std::function<bool()> active; std::function<void()> click; int w; };
    void addTab (juce::String label, std::function<bool()> active,
                 std::function<void()> click, int w = 0)
    {
        tabs.push_back ({ std::move (label), std::move (active), std::move (click), w });
        resized();
    }

    /** Reserve a slot immediately left of the tabs (e.g. for a division combo).
        Returns its bounds so the editor can place a child component there. */
    void setReservedWidth (int w) { reservedW = w; resized(); }
    juce::Rectangle<int> reservedBounds() const { return reservedRect; }

    //==============================================================================
    void resized() override { layout(); }

    void paint (juce::Graphics& g) override
    {
        using P = Palette;
        if (drawBg)
        {
            g.fillAll (P::bgTop.brighter (0.05f));
            g.setColour (P::panelEdge.withAlpha (0.75f));
            g.fillRect (0, getHeight() - 1, getWidth(), 1);
        }

        // ---- title ----
        g.setColour (P::text);
        g.setFont (juce::Font (juce::FontOptions (16.0f).withStyle ("Bold")));
        g.drawText (title, titleRect, juce::Justification::centredLeft);
        if (subtitle.isNotEmpty())
        {
            g.setColour (P::accent.withAlpha (0.85f));
            g.setFont (juce::Font (juce::FontOptions (8.5f).withStyle ("Bold")));
            g.drawText (subtitle.toUpperCase(),
                        titleRect.withTrimmedTop (titleRect.getHeight() - 12).translated (1, 2),
                        juce::Justification::centredLeft);
        }

        // ---- preset pill ----
        if (presetCount && presetCount() > 0)
        {
            drawArrow (g, prevRect, juce::CharPointer_UTF8 ("\xe2\x97\x80"), hover == Zone::Prev);
            drawArrow (g, nextRect, juce::CharPointer_UTF8 ("\xe2\x96\xb6"), hover == Zone::Next);

            const bool hov = hover == Zone::Pill;
            g.setColour (hov ? P::accent.withAlpha (0.20f) : P::track);
            g.fillRoundedRectangle (pillRect.toFloat(), 4.0f);
            g.setColour (P::panelEdge.brighter (0.2f));
            g.drawRoundedRectangle (pillRect.toFloat().reduced (0.5f), 4.0f, 1.0f);

            juce::String name = (presetName ? presetName (presetIndex ? presetIndex() : 0) : juce::String());
            name += "   " + juce::String (juce::CharPointer_UTF8 ("\xe2\x96\xbe"));
            g.setFont (juce::Font (juce::FontOptions (11.0f).withStyle ("Bold")));
            g.setColour (P::text);
            g.drawText (name, pillRect.reduced (8, 0), juce::Justification::centred);
        }

        // ---- tabs ----
        for (size_t i = 0; i < tabs.size(); ++i)
            drawTabBtn (g, tabRects[i], tabs[i].label,
                        tabs[i].active && tabs[i].active(),
                        hover == Zone::Tab && hoverIdx == (int) i);
    }

    void mouseMove (const juce::MouseEvent& e) override
    {
        auto z = zoneFor (e.getPosition());
        if (z.first != hover || z.second != hoverIdx) { hover = z.first; hoverIdx = z.second; repaint(); }
    }
    void mouseExit (const juce::MouseEvent&) override
    {
        if (hover != Zone::None) { hover = Zone::None; hoverIdx = -1; repaint(); }
    }
    void mouseDown (const juce::MouseEvent& e) override
    {
        auto [z, idx] = zoneFor (e.getPosition());
        const int n = (presetCount ? presetCount() : 0);
        switch (z)
        {
            case Zone::Prev: if (selectPreset && n > 0) selectPreset ((presetIndex() + n - 1) % n); break;
            case Zone::Next: if (selectPreset && n > 0) selectPreset ((presetIndex() + 1) % n); break;
            case Zone::Pill: showPresetMenu(); break;
            case Zone::Tab:  if (idx >= 0 && idx < (int) tabs.size() && tabs[(size_t) idx].click) tabs[(size_t) idx].click(); repaint(); break;
            default: break;
        }
    }

private:
    enum class Zone { None, Prev, Pill, Next, Tab };

    juce::String title, subtitle;
    std::vector<Tab> tabs;
    int reservedW = 0;

    juce::Rectangle<int> titleRect, prevRect, pillRect, nextRect, reservedRect;
    std::vector<juce::Rectangle<int>> tabRects;

    Zone hover = Zone::None;
    int  hoverIdx = -1;
    bool drawBg = true;

    void layout()
    {
        const int H = getHeight(), W = getWidth();
        const int btnH = 26, btnY = (H - btnH) / 2;

        titleRect = { 14, 0, 190, H };

        // tabs from the right edge, leftward
        tabRects.assign (tabs.size(), {});
        int totalW = 0;
        std::vector<int> ws (tabs.size());
        for (size_t i = 0; i < tabs.size(); ++i)
        {
            const int w = tabs[i].w > 0 ? tabs[i].w
                        : juce::jmax (54, (int) (tabs[i].label.length() * 7.4f) + 20);
            ws[i] = w; totalW += w + (i ? 4 : 0);
        }
        int x = W - 8 - totalW;
        const int tabsStartX = x;
        for (size_t i = 0; i < tabs.size(); ++i)
        {
            tabRects[i] = { x, btnY, ws[i], btnH };
            x += ws[i] + 4;
        }

        // reserved slot (division combo) just left of the tabs
        if (reservedW > 0)
            reservedRect = { tabsStartX - 8 - reservedW, btnY, reservedW, btnH };
        else
            reservedRect = {};

        // preset group centred between the title and the reserved/tabs cluster
        const int leftEdge  = titleRect.getRight() + 12;
        const int rightEdge = (reservedW > 0 ? reservedRect.getX() : tabsStartX) - 12;
        constexpr int aw = 22, pw = 150, gap = 3;
        const int groupW = aw + gap + pw + gap + aw;
        const int gx = juce::jmax (leftEdge, leftEdge + ((rightEdge - leftEdge) - groupW) / 2);
        prevRect = { gx, btnY, aw, btnH };
        pillRect = { gx + aw + gap, btnY, pw, btnH };
        nextRect = { gx + aw + gap + pw + gap, btnY, aw, btnH };
    }

    std::pair<Zone,int> zoneFor (juce::Point<int> p) const
    {
        if (prevRect.contains (p)) return { Zone::Prev, -1 };
        if (pillRect.contains (p)) return { Zone::Pill, -1 };
        if (nextRect.contains (p)) return { Zone::Next, -1 };
        for (size_t i = 0; i < tabRects.size(); ++i)
            if (tabRects[i].contains (p)) return { Zone::Tab, (int) i };
        return { Zone::None, -1 };
    }

    void drawArrow (juce::Graphics& g, juce::Rectangle<int> r, juce::String glyph, bool hov)
    {
        using P = Palette;
        if (hov) { g.setColour (P::accent.withAlpha (0.15f)); g.fillRoundedRectangle (r.toFloat(), 4.0f); }
        g.setFont (juce::Font (juce::FontOptions (12.0f)));
        g.setColour (hov ? P::accent : P::textDim);
        g.drawText (glyph, r, juce::Justification::centred);
    }

    void drawTabBtn (juce::Graphics& g, juce::Rectangle<int> r,
                     const juce::String& label, bool active, bool hovered)
    {
        using P = Palette;
        const auto rf = r.toFloat();
        if (active)
        {
            g.setColour (P::accent.withAlpha (0.22f)); g.fillRoundedRectangle (rf, 4.0f);
            g.setColour (P::accent.withAlpha (0.65f)); g.drawRoundedRectangle (rf.reduced (0.5f), 4.0f, 1.0f);
        }
        else if (hovered)
        {
            g.setColour (P::accent.withAlpha (0.10f)); g.fillRoundedRectangle (rf, 4.0f);
            g.setColour (P::track.brighter (0.4f));    g.drawRoundedRectangle (rf.reduced (0.5f), 4.0f, 1.0f);
        }
        else
        {
            g.setColour (P::track); g.drawRoundedRectangle (rf.reduced (0.5f), 4.0f, 1.0f);
        }
        g.setFont (juce::Font (juce::FontOptions (11.0f).withStyle ("Bold")));
        g.setColour (active ? P::accent : (hovered ? P::accent.withAlpha (0.85f) : P::text.withAlpha (0.72f)));
        g.drawText (label, r, juce::Justification::centred);
    }

    void showPresetMenu()
    {
        if (! presetCount || ! selectPreset) return;
        const int n = presetCount();
        const int cur = presetIndex ? presetIndex() : 0;
        juce::PopupMenu menu;
        for (int i = 0; i < n; ++i)
            menu.addItem (i + 1, presetName ? presetName (i) : juce::String (i), true, i == cur);
        juce::Component::SafePointer<PluginTopBar> safe (this);
        menu.showMenuAsync (juce::PopupMenu::Options().withTargetComponent (this)
                                .withMinimumWidth (pillRect.getWidth()),
            [safe] (int r) { if (r > 0 && safe != nullptr && safe->selectPreset) safe->selectPreset (r - 1); });
    }

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (PluginTopBar)
};

} // namespace schurUi
