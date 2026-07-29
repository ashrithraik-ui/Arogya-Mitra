import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ChevronDown, Calendar, FileText, Pill, ImageIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export interface TimelineEvent {
  id: string;
  date: string;
  type: 'consultation' | 'report' | 'prescription' | 'image';
  title: string;
  summary: string;
  details: string;
}

interface TimelineProps {
  events: TimelineEvent[];
}

const typeConfig = {
  consultation: { icon: Calendar, color: 'text-blue-500', bg: 'bg-blue-500/10' },
  report: { icon: FileText, color: 'text-cyan-500', bg: 'bg-cyan-500/10' },
  prescription: { icon: Pill, color: 'text-purple-500', bg: 'bg-purple-500/10' },
  image: { icon: ImageIcon, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
};

export function Timeline({ events }: TimelineProps) {
  const [expandedId, setExpandedId] = React.useState<string | null>(null);

  return (
    <div className="relative pl-6 space-y-8 before:absolute before:inset-0 before:ml-[1.1rem] before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-muted before:to-transparent">
      {events.map((event, index) => {
        const config = typeConfig[event.type];
        const Icon = config.icon;
        const isExpanded = expandedId === event.id;

        return (
          <div key={event.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
            {/* Timeline Dot */}
            <div className={`flex items-center justify-center w-10 h-10 rounded-full border-4 border-background ${config.bg} ${config.color} shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 shadow-sm z-10 absolute left-[-2rem] md:left-1/2`}>
              <Icon className="w-4 h-4" />
            </div>

            {/* Content Card */}
            <div className="w-[calc(100%-2rem)] md:w-[calc(50%-2.5rem)]">
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.1 }}>
                <Card className="hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-2">
                      <h4 className="font-semibold text-lg">{event.title}</h4>
                      <time className="text-xs font-medium text-muted-foreground">{event.date}</time>
                    </div>
                    <p className="text-sm text-foreground/80 mb-3">{event.summary}</p>
                    
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="overflow-hidden"
                        >
                          <div className="pt-3 border-t mt-3 text-sm bg-muted/50 p-3 rounded-md">
                            {event.details}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>

                    <Button 
                      variant="ghost" 
                      size="sm" 
                      className="w-full mt-2 h-8 text-xs text-muted-foreground hover:text-primary"
                      onClick={() => setExpandedId(isExpanded ? null : event.id)}
                    >
                      {isExpanded ? 'Hide Details' : 'View Details'}
                      <motion.div animate={{ rotate: isExpanded ? 180 : 0 }} className="ml-1">
                        <ChevronDown className="w-4 h-4" />
                      </motion.div>
                    </Button>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
