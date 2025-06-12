from utils.logger import logger
from typing import Any, Dict, List, Optional
from datetime import datetime
from database.connection import BaseRepository

class KostRepository:
    def __init__(self):
        self.table_name = "kosts"

    async def insert_kost(
        self,
        conn: Any,
        name: str,
        address: str,
        city: str,
        region: str,
        rules: Optional[str] = None,
        created_at: Optional[datetime] = None
    ) -> int:
        """
        Insert a new kost into the kosts table.

        Args:
            conn: Database connection object.
            name: Name of the kost.
            address: Address of the kost.
            city: City where the kost is located.
            region: Region of the kost.
            rules: Optional rules for the kost.
            created_at: Optional creation timestamp.

        Returns:
            The inserted kost_id.
        """
        if not name or not address or not city or not region:
            logger.error("Missing required fields for inserting kost")
            raise ValueError("name, address, city, and region are required")

        data: Dict[str, Any] = {
            "name": name,
            "address": address,
            "city": city,
            "region": region,
            "rules": rules
        }
        if created_at:
            data["created_at"] = created_at

        try:
            repo = BaseRepository(self.table_name)
            kost_id = await repo.insert(conn, data)
            logger.info(f"Inserted kost with id {kost_id}")
            return kost_id
        except Exception as e:
            logger.error(f"Failed to insert kost: {e}")
            raise

    async def get_kosts(
        self,
        conn: Any,
        city: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 10,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve kosts, optionally filtered by city and/or region.

        Args:
            conn: Database connection object.
            city: Optional city filter.
            region: Optional region filter.
            limit: Number of kosts to retrieve.
            offset: Number of kosts to skip.

        Returns:
            List of kost records.
        """
        try:
            repo = BaseRepository(self.table_name)
            query = f"SELECT * FROM {self.table_name}"
            params = []
            filters = []

            if city:
                filters.append("city = %s")
                params.append(city)
            if region:
                filters.append("region = %s")
                params.append(region)

            if filters:
                query += " WHERE " + " AND ".join(filters)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            rows = await repo.fetch_all(conn, query, tuple(params))
            logger.info(f"Retrieved {len(rows)} kost(s)")
            return rows
        except Exception as e:
            logger.error(f"Failed to retrieve kosts: {e}")
            raise