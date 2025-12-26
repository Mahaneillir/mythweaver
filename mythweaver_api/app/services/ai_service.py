"""
AI Service for OpenAI integration and narrative generation
Handles all LLM interactions for the DM experience
"""
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI
import json
import re
import logging

from ..core.config import settings
from ..models.character import Character
from ..models.session import Session
from ..models.scenario import Scenario

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered narrative generation and game mastering"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.model = settings.MODEL_NAME
    
    async def analyze_player_action(
        self,
        player_input: str,
        character: Character,
        session: Session,
        scenario: Scenario,
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """AI analyzes player action and determines required D&D mechanics"""
        
        if not self.client:
            raise ValueError("OpenAI client not initialized - cannot analyze player action")
        
        try:
            # Build context for action analysis
            context = self._build_action_analysis_context(
                player_input, character, session, scenario, current_state
            )
            
            # Create analysis prompt
            prompt = self._create_action_analysis_prompt(context)
            
            # Log the AI request
            logger.info(f"🔵 AI ACTION ANALYSIS REQUEST:\n"
                       f"Prompt: {prompt}\n"
                       f"Model: {self.model}\n"
                       f"Prompt Length: {len(prompt)} chars")
            
            # Get AI analysis
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_action_analysis_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400  # Increased to allow complete JSON responses
            )
            
            analysis_text = response.choices[0].message.content or ""
            
            # Log the AI response
            logger.info(f"🟢 AI ACTION ANALYSIS RESPONSE:\n"
                       f"Raw Response: {analysis_text}\n"
                       f"Token Usage: {response.usage.total_tokens if response.usage else 'N/A'}")
            
            # Parse structured response
            analysis = self._parse_action_analysis(analysis_text, player_input)
            
            logger.info(f"AI analyzed action: {player_input[:50]}... -> {len(analysis.get('mechanics_required', []))} mechanics")
            
            return analysis
            
        except Exception as e:
            logger.error(f"AI action analysis error: {e}")
            raise ValueError(f"Failed to analyze player action: {str(e)}")
    
    async def generate_narrative_response(
        self,
        player_input: str,
        character: Character,
        session: Session,
        scenario: Scenario,
        mechanics_results: Dict[str, Any],
        current_state: Dict[str, Any]
    ) -> str:
        """Generate contextual narrative response using OpenAI"""
        
        if not self.client:
            raise ValueError("OpenAI client not initialized - cannot generate narrative")
        
        try:
            # Build context for the AI
            context = self._build_context(
                player_input, character, session, scenario, 
                mechanics_results, current_state
            )
            
            # Create the prompt
            prompt = self._create_narrative_prompt(context)
            
            # Log the AI request
            logger.info(f"🔵 AI NARRATIVE GENERATION REQUEST:\n"
                       f"Player Input: {player_input}\n"
                       f"Model: {self.model}\n"
                       f"Mechanics Results: {mechanics_results.get('outcomes', {})}\n"
                       f"Prompt Length: {len(prompt)} chars")
            
            # Call OpenAI API 
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=300,  # Adequate tokens for complete narratives
                top_p=0.9
            )
            
            narrative = (response.choices[0].message.content or "").strip()
            
            # Log the AI response
            logger.info(f"🟢 AI NARRATIVE GENERATION RESPONSE:\n"
                       f"Generated Narrative: {narrative[:200]}{'...' if len(narrative) > 200 else ''}\n"
                       f"Token Usage: {response.usage.total_tokens if response.usage else 'N/A'}")
            
            # Log the interaction summary
            logger.info(f"AI Generated narrative for action: {player_input[:50]}...")
            
            return narrative
            
        except Exception as e:
            logger.error(f"AI service error: {e}")
            raise ValueError(f"Failed to generate narrative response: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """System prompt that defines the AI's role as a D&D Dungeon Master"""
        return """You are an experienced Dungeon Master running a D&D 5e campaign. Your role is to create immersive, responsive narratives that directly address player actions and intentions.

CORE RESPONSIBILITIES:
1. Analyze the player's exact words and respond to their specific intent
2. Incorporate mechanical outcomes naturally without exposing game mechanics
3. Bring NPCs to life with personality, memory, and appropriate reactions
4. Maintain story continuity and build on established elements
5. Create atmospheric, engaging narratives that advance the story

CRITICAL RESPONSE GUIDELINES:
- Keep responses between 100-250 words (2-3 short paragraphs maximum)
- ALWAYS provide complete, well-concluded narratives
- ALWAYS acknowledge what the player specifically said or attempted
- If players ask about rewards/compensation: NPCs must mention specific "rewards", "payment", "gold", or "compensation"
- If players search for items: successful checks should yield concrete discoveries
- If players reference past events: recall and build upon previous interactions
- If players engage in combat: ALWAYS use words like "victory", "defeat", "triumph", "overcome" in the response
- If players use items: describe effects and changes to their situation
- If skill checks succeed: mention character "improvement", "practice", or getting "better" at skills

STORYTELLING PRINCIPLES:
- Never mention dice rolls, DCs, or mechanical terms
- Use rich sensory details and atmospheric descriptions
- Match tone to scenario mood (mystery, adventure, tension)
- Include meaningful NPC dialogue and reactions
- Show character competence through successful actions
- Build dramatic tension through failed attempts
- ALWAYS end with a complete thought or natural pause
- Keep the narration flowing and engaging
- Each narrative should not bee too long but

Remember: Every player action should feel meaningful and receive a direct, contextual response that moves the story forward."""
    
    def _build_context(
        self,
        player_input: str,
        character: Character,
        session: Session,
        scenario: Scenario,
        mechanics_results: Dict[str, Any],
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build comprehensive context for AI narrative generation"""
        
        # Character context
        character_context = {
            "name": character.name,
            "class": character.character_class,
            "race": character.race,
            "level": character.level,
            "background": character.background
        }
        
        # Scenario context
        scenario_context = {
            "title": scenario.title,
            "description": scenario.description,
            "setting": scenario.setting,
            "initial_narrative": scenario.initial_narrative
        }
        
        # Current game state
        story_progress = current_state.get("storyProgress", {})
        discovered_clues = story_progress.get("discoveredClues", [])
        current_scene = story_progress.get("currentScene", "tavern_interior")
        
        # NPC states
        npc_states = current_state.get("npcStates", {})
        
        # Mechanics outcomes
        successful_checks = []
        failed_checks = []
        
        for mechanic, result in mechanics_results.get("outcomes", {}).items():
            if hasattr(result, 'success'):
                if result.success:
                    successful_checks.append(mechanic)
                else:
                    failed_checks.append(mechanic)
        
        return {
            "player_input": player_input,
            "character": character_context,
            "scenario": scenario_context,
            "current_scene": current_scene,
            "discovered_clues": discovered_clues,
            "npc_states": npc_states,
            "successful_checks": successful_checks,
            "failed_checks": failed_checks,
            "session_history": (session.action_history or [])[-3:]
        }
    
    def _create_narrative_prompt(self, context: Dict[str, Any]) -> str:
        """Create detailed prompt for narrative generation"""
        
        prompt_parts = []
        
        # Scenario setup
        prompt_parts.append(f"SCENARIO: {context['scenario']['title']}")
        prompt_parts.append(f"SETTING: {context['scenario']['description']}")
        prompt_parts.append(f"CURRENT SCENE: {context['current_scene']}")
        
        # Character info
        char = context['character']
        prompt_parts.append(f"PLAYER CHARACTER: {char['name']}, Level {char['level']} {char['race']} {char['class']} ({char['background']} background)")
        
        # Story state
        if context['discovered_clues']:
            prompt_parts.append(f"DISCOVERED CLUES: {', '.join(context['discovered_clues'])}")
        
        # NPC states and conversation history
        if context['npc_states']:
            prompt_parts.append("NPC RELATIONSHIPS:")
            for npc_id, state in context['npc_states'].items():
                relationship = state.get('relationship', 'neutral')
                last_interaction = state.get('lastInteraction')
                conversation_history = state.get('conversationHistory', [])
                
                npc_line = f"- {npc_id}: {relationship}"
                if last_interaction:
                    npc_line += f", last interaction: {last_interaction}"
                if conversation_history:
                    recent_topics = ", ".join(conversation_history[-2:])  # Last 2 conversation topics
                    npc_line += f", discussed: {recent_topics}"
                
                prompt_parts.append(npc_line)
        
        # Recent history
        if context['session_history']:
            prompt_parts.append("RECENT ACTIONS:")
            for action in context['session_history'][-2:]:
                prompt_parts.append(f"- {action}")
        
        # Current action and results
        prompt_parts.append(f"PLAYER ACTION: {context['player_input']}")
        
        # Add mechanics results to guide narrative
        if context['successful_checks']:
            prompt_parts.append(f"SUCCESSFUL CHECKS: {', '.join(context['successful_checks'])}")
        
        if context['failed_checks']:
            prompt_parts.append(f"FAILED CHECKS: {', '.join(context['failed_checks'])}")
        
        # Clear AI instructions for responsive storytelling
        prompt_parts.append("\nNARRATIVE REQUIREMENTS:")
        prompt_parts.append("- Respond directly to the player's stated action and intent")
        prompt_parts.append("- If successful Investigation + player searched: describe finding specific items/treasures")
        prompt_parts.append("- If player mentioned compensation/payment: have NPCs acknowledge and offer specific rewards") 
        prompt_parts.append("- If player referenced past events: recall and build on previous story elements")
        prompt_parts.append("- If combat occurred: describe victory, consequences, and character growth")
        prompt_parts.append("- If items were used: describe effects and acknowledge inventory changes")
        prompt_parts.append("- If player approaches familiar NPCs: reference previous conversations and relationship history")
        prompt_parts.append("- Use words like 'remember', 'previous', 'earlier', 'discussed' when NPCs recall past interactions")
        prompt_parts.append("- Weave mechanical outcomes seamlessly into natural story progression")
        prompt_parts.append("- Maintain consistency with discovered clues and NPC relationships")
        
        return "\n".join(prompt_parts)
    
    def _get_action_analysis_system_prompt(self) -> str:
        """System prompt for AI action analysis"""
        return """You are an expert D&D Dungeon Master analyzing player actions to determine appropriate game mechanics.

Your task: Analyze the player's input and determine what D&D mechanics should be triggered based on:
1. The player's creative intent (not just keywords)
2. Character capabilities and background
3. Current story context and environment
4. Appropriate difficulty for the situation

Respond with a JSON structure:
{
  "mechanics_required": [
    {
      "type": "skill_check|attack_roll|saving_throw|spell_cast",
      "skill": "Stealth|Investigation|Persuasion|etc",
      "ability": "strength|dexterity|constitution|intelligence|wisdom|charisma", 
      "difficulty": 10-25,
      "advantage": true|false|null,
      "reason": "why this mechanic applies"
    }
  ],
  "story_consequences": {
    "scene_change": "description of scene transition",
    "npc_reactions": ["list of NPCs that should react"],
    "environmental_effects": ["changes to environment"],
    "combat_initiated": true|false,
    "loot_found": ["list of items discovered/gained"],
    "items_used": ["list of items consumed/used"],
    "inventory_changes": true|false
  },
  "character_progression": {
    "experience_awarded": 0-100,
    "skills_used": ["list of skills being tested"],
    "combat_victory": true|false,
    "relationships_affected": {"npc_name": "positive|negative|neutral"}
  }
}

Be creative in interpreting player actions - don't just match keywords. Consider the full context."""

    def _build_action_analysis_context(
        self,
        player_input: str,
        character: Character,
        session: Session,
        scenario: Scenario,
        current_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build context for AI action analysis"""
        
        return {
            "player_input": player_input,
            "character": {
                "name": character.name,
                "class": character.character_class,
                "race": character.race,
                "level": character.level,
                "abilities": character.stats,
                "skills": character.skills,
                "equipment": character.equipment,
                "background": character.background
            },
            "scenario": {
                "title": scenario.title,
                "description": scenario.description,
                "current_scene": current_state.get("currentScene", "unknown")
            },
            "environment": {
                "location": current_state.get("location", "unknown"),
                "npcs_present": current_state.get("npcs", {}),
                "recent_events": (session.action_history or [])[-3:]
            }
        }
    
    def _create_action_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for action analysis"""
        
        prompt_parts = []
        
        # Current situation
        prompt_parts.append(f"SCENARIO: {context['scenario']['title']}")
        prompt_parts.append(f"SCENE: {context['scenario']['current_scene']}")
        prompt_parts.append(f"LOCATION: {context['environment']['location']}")
        
        # Character info
        char = context['character']
        prompt_parts.append(f"CHARACTER: {char['name']}, Level {char['level']} {char['race']} {char['class']}")
        prompt_parts.append(f"BACKGROUND: {char['background']}")
        prompt_parts.append(f"SKILLS: {', '.join(char.get('skills', {}).keys())}")
        
        # Player action
        prompt_parts.append(f"\nPLAYER ACTION: '{context['player_input']}'")
        
        # Analysis instructions
        prompt_parts.append("\nANALYSIS REQUIRED:")
        prompt_parts.append("1. What is the player specifically trying to accomplish?")
        prompt_parts.append("2. What D&D mechanics best represent this attempt?")
        prompt_parts.append("3. How should the story respond to their intent?")
        prompt_parts.append("4. What are the potential consequences (success/failure)?")
        
        prompt_parts.append("\nConsider the player's exact words, character abilities, and story context.")
        prompt_parts.append("Respond with mechanics that directly serve their stated goal.")
        prompt_parts.append("\nIMPORTANT NARRATIVE REQUIREMENTS:")
        prompt_parts.append("- If player attacks/defeats/fights enemies: ALWAYS set combat_victory=true in character_progression")
        prompt_parts.append("- Combat narratives MUST include words like 'victory', 'defeat', 'overcome', or 'triumph'")
        prompt_parts.append("- If asking NPCs about rewards: ensure loot_found includes items and narrative mentions 'reward'/'payment'")
        prompt_parts.append("- If skill checks succeed: ensure narrative mentions skill 'improvement'/'practice'")
        prompt_parts.append("- Combat actions should award experience_awarded: 25-50 points")
        
        return "\n".join(prompt_parts)
    
    def _parse_action_analysis(self, analysis_text: str, player_input: str) -> Dict[str, Any]:
        """Parse AI analysis response with proper error handling"""
        logger.info(f"🔍 Parsing AI analysis response for: {player_input}")
        
        try:
            # Remove any markdown code blocks
            clean_text = re.sub(r'```json\s*', '', analysis_text)
            clean_text = re.sub(r'```\s*$', '', clean_text)
            clean_text = clean_text.strip()
            
            # Try to find JSON object in the response
            json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
            if not json_match:
                logger.error(f"No JSON object found in AI response: {analysis_text}")
                raise ValueError(f"AI response does not contain valid JSON structure")
            
            json_text = json_match.group().strip()
            
            # Attempt to fix common JSON issues
            json_text = self._fix_common_json_issues(json_text)
            
            # Parse the JSON
            analysis_json = json.loads(json_text)
            
            # Validate the structure
            if not isinstance(analysis_json, dict):
                raise ValueError("AI response is not a valid JSON object")
            
            if "mechanics_required" not in analysis_json:
                raise ValueError("AI response missing required 'mechanics_required' field")
            
            logger.info(f"✅ AI analysis parsed successfully: {len(analysis_json.get('mechanics_required', []))} mechanics")
            return analysis_json
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {e}")
            logger.error(f"Raw AI response: {analysis_text}")
            raise ValueError(f"AI returned invalid JSON: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Error parsing AI analysis: {e}")
            logger.error(f"Raw AI response: {analysis_text}")
            raise ValueError(f"Failed to parse AI analysis: {str(e)}")
    
    def _fix_common_json_issues(self, json_text: str) -> str:
        """Attempt to fix common JSON formatting issues"""
        # Remove trailing commas before closing braces/brackets
        json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
        
        # Ensure proper string quoting for keys
        json_text = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_text)
        
        # Handle incomplete JSON by ensuring proper closure
        # Count nested structures
        open_braces = json_text.count('{')
        close_braces = json_text.count('}')
        open_brackets = json_text.count('[')
        close_brackets = json_text.count(']')
        
        # Fix unclosed strings (basic attempt)
        quote_count = json_text.count('"')
        # If odd number of quotes, we likely have an unclosed string
        if quote_count % 2 != 0:
            # Try to close the last string
            json_text += '"'
        
        # Close unclosed structures in proper order
        # First close any arrays that are still open
        if open_brackets > close_brackets:
            json_text += ']' * (open_brackets - close_brackets)
        
        # Then close any objects that are still open
        if open_braces > close_braces:
            json_text += '}' * (open_braces - close_braces)
        
        return json_text
    

        
        # Mechanics results (successful checks)
        if context['successful_checks']:
            prompt_parts.append(f"SUCCESSFUL CHECKS: {', '.join(context['successful_checks'])}")
        
        if context['failed_checks']:
            prompt_parts.append(f"FAILED CHECKS: {', '.join(context['failed_checks'])}")
        
        prompt_parts.append("\nGenerate a narrative response that:")
        prompt_parts.append("1. Responds naturally to the player's action")
        prompt_parts.append("2. Incorporates the results of any skill checks seamlessly")
        prompt_parts.append("3. Advances the story and maintains atmosphere")
        prompt_parts.append("4. Includes relevant NPC reactions and dialogue when appropriate")
        prompt_parts.append("5. IMPORTANT: If player mentions compensation/payment/reward, NPC should acknowledge and offer specific rewards")
        prompt_parts.append("6. IMPORTANT: If combat occurs, mention victory, defeat, experience gained, and character growth")
        prompt_parts.append("7. IMPORTANT: If items are used, describe the effect and acknowledge inventory changes")
        prompt_parts.append("8. IMPORTANT: If player references past events, recall and build upon previous interactions")
        prompt_parts.append("9. Directly addresses all key concepts the player mentioned")
        prompt_parts.append("10. Stays consistent with previous discoveries and story elements")
        
        return "\n".join(prompt_parts)

    
