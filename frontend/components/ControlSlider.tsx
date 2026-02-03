export default function ControlSlider({ label, value, min, max, unit, onChange }: { label: string, value: number, min: number, max: number, unit?: string, onChange?: (val: number) => void }) {
    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <span className="text-sm font-medium">{label}</span>
                <span className="text-sm text-muted-foreground font-mono">{value}{unit}</span>
            </div>
            <div className="relative w-full h-2">
                <input
                    type="range"
                    min={min}
                    max={max}
                    step={unit ? 0.1 : 1}
                    value={value}
                    onChange={(e) => onChange && onChange(parseFloat(e.target.value))}
                    className="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
                />
            </div>
            <div className="flex justify-between text-xs text-muted-foreground">
                <span>{min}{unit}</span>
                <span>{max}{unit}</span>
            </div>
        </div>
    );
}
